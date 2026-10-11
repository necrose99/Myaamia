<?xml version="1.0" encoding="UTF-8"?>
<!--
  eaf-to-lift.xsl
  Extracts a LIFT 0.13 lexicon from an ELAN .eaf fieldwork file.

  Bridges the ELAN fieldwork world (audio-aligned transcripts) to the
  SIL LIFT dictionary world (structured lexical entries).

  Each unique orthographic word type found in the orth tier becomes
  one LIFT <entry>. Per-word information is aggregated across all
  utterances where the word occurs.

  Mapping:
    orth tier     → <lexical-unit><form>
    ipa tier      → <pronunciation><form lang="X-fonipa">
    gloss tier    → <sense><gloss> (Leipzig gloss tokens → senses)
    trans tier(s) → <sense><gloss lang="xx"> (free translations)
    etym JSON     → <etymology> (LIFT custom field — reconstructed as <note type="etym">)
    morph tier    → <note type="morph-segmentation">
    psych tier    → <note type="psychoacoustic"> (its:translate="no")
    example sent  → <sense><example><form> + <translation>

  DMLex etymonUnit fields (langCode, text, reconstructed, translation)
  are parsed out of the JSON blob stored in the EAF etym tier and
  mapped to LIFT <etymology> fields.
-->
<xsl:stylesheet
  xmlns:xsl  = "http://www.w3.org/1999/XSL/Transform"
  xmlns:its  = "http://www.w3.org/2005/11/its"
  version    = "2.0">

  <xsl:output method="xml" encoding="UTF-8" indent="yes"/>
  <xsl:strip-space elements="*"/>

  <xsl:param name="source-lang"   select="'und'"/>
  <xsl:param name="target-lang"   select="'en'"/>
  <xsl:param name="orth-tier"     select="'orth'"/>
  <xsl:param name="ipa-tier"      select="'ipa'"/>
  <xsl:param name="morph-tier"    select="'morph'"/>
  <xsl:param name="gloss-tier"    select="'gloss'"/>
  <xsl:param name="trans-prefix"  select="'trans-'"/>
  <xsl:param name="etym-tier"     select="'etym'"/>
  <xsl:param name="psych-tier"    select="'psych'"/>
  <xsl:param name="lift-version"  select="'0.13'"/>

  <xsl:key name="ref-by-parent"  match="ANNOTATION/REF_ANNOTATION" use="@ANNOTATION_REF"/>
  <xsl:key name="ts-by-id"       match="TIME_SLOT"                  use="@TIME_SLOT_ID"/>

  <!-- ============================================================
       Root → LIFT
       ============================================================ -->
  <xsl:template match="/ANNOTATION_DOCUMENT">
    <xsl:variable name="all-orth-anns"
      select="//TIER[starts-with(@TIER_ID,$orth-tier)]
                //ANNOTATION/REF_ANNOTATION"/>

    <lift version="{$lift-version}"
          producer="eaf-to-lift.xsl"
          xmlns:its="http://www.w3.org/2005/11/its"
          its:version="1.0">

      <!-- ITS rules -->
      <xsl:processing-instruction name="ITS-rules">
        translate="no": pronunciation, note[@type='morph-segmentation'],
        note[@type='psychoacoustic'], note[@type='etym']
      </xsl:processing-instruction>

      <!-- Group by orthographic headword type -->
      <xsl:for-each-group select="$all-orth-anns"
                          group-by="ANNOTATION_VALUE">
        <xsl:sort select="current-grouping-key()"/>

        <xsl:variable name="headword"   select="current-grouping-key()"/>
        <xsl:variable name="first"      select="current-group()[1]"/>
        <xsl:variable name="first-id"   select="$first/@ANNOTATION_ID"/>
        <xsl:variable name="parent-id"  select="$first/@ANNOTATION_REF"/>

        <!-- Gather child tiers of first occurrence -->
        <xsl:variable name="ipa"
          select="key('ref-by-parent',$first-id)
                      [ancestor::TIER[starts-with(@TIER_ID,$ipa-tier)]][1]
                      /ANNOTATION_VALUE"/>
        <xsl:variable name="morph"
          select="key('ref-by-parent',$first-id)
                      [ancestor::TIER[starts-with(@TIER_ID,$morph-tier)]][1]
                      /ANNOTATION_VALUE"/>
        <xsl:variable name="morph-id"
          select="key('ref-by-parent',$first-id)
                      [ancestor::TIER[starts-with(@TIER_ID,$morph-tier)]][1]
                      /@ANNOTATION_ID"/>
        <xsl:variable name="gloss"
          select="key('ref-by-parent',$morph-id)
                      [ancestor::TIER[starts-with(@TIER_ID,$gloss-tier)]][1]
                      /ANNOTATION_VALUE"/>
        <xsl:variable name="etym-json"
          select="key('ref-by-parent',$first-id)
                      [ancestor::TIER[starts-with(@TIER_ID,$etym-tier)]][1]
                      /ANNOTATION_VALUE"/>

        <!-- Translations from first occurrence's parent utterance -->
        <xsl:variable name="trans-anns"
          select="key('ref-by-parent',$parent-id)
                      [ancestor::TIER[starts-with(@TIER_ID,$trans-prefix)]]"/>

        <entry id="{concat('e_',$source-lang,'_',
                           encode-for-uri($headword),'_',
                           generate-id($first))}">

          <lexical-unit>
            <form lang="{$source-lang}">
              <text><xsl:value-of select="$headword"/></text>
            </form>
          </lexical-unit>

          <!-- Pronunciation (IPA) — its:translate="no" -->
          <xsl:if test="normalize-space($ipa)!=''">
            <pronunciation>
              <form lang="{concat($source-lang,'-fonipa')}">
                <text its:translate="no"><xsl:value-of select="$ipa"/></text>
              </form>
            </pronunciation>
          </xsl:if>

          <!-- Morpheme segmentation as note -->
          <xsl:if test="normalize-space($morph)!=''">
            <note type="morph-segmentation"
                  its:translate="no"><xsl:value-of select="$morph"/></note>
          </xsl:if>

          <!-- SENSE: built from gloss tier + translations -->
          <sense id="{concat('s_',generate-id($first))}">

            <!-- Interlinear gloss → LIFT <gloss> per Leipzig token -->
            <xsl:if test="normalize-space($gloss)!=''">
              <xsl:for-each select="tokenize(normalize-space($gloss),'\s{2,}')">
                <gloss lang="{$target-lang}">
                  <text><xsl:value-of select="normalize-space(.)"/></text>
                </gloss>
              </xsl:for-each>
            </xsl:if>

            <!-- Free translations from trans tiers -->
            <xsl:for-each select="$trans-anns">
              <xsl:variable name="tl"
                select="if (contains(substring-after(ancestor::TIER/@TIER_ID,$trans-prefix),'@'))
                        then substring-before(
                               substring-after(ancestor::TIER/@TIER_ID,$trans-prefix),'@')
                        else substring-after(ancestor::TIER/@TIER_ID,$trans-prefix)"/>
              <xsl:if test="normalize-space(ANNOTATION_VALUE)!=''">
                <gloss lang="{$tl}">
                  <text><xsl:value-of select="ANNOTATION_VALUE"/></text>
                </gloss>
              </xsl:if>
            </xsl:for-each>

            <!-- Examples: one per occurrence in the corpus -->
            <xsl:for-each select="current-group()">
              <xsl:variable name="eg-orth"      select="ANNOTATION_VALUE"/>
              <xsl:variable name="eg-parent-id" select="@ANNOTATION_REF"/>

              <!-- Full utterance orth for context -->
              <xsl:variable name="utterance-orth-text"
                select="key('ref-by-parent',$eg-parent-id)
                            [ancestor::TIER[starts-with(@TIER_ID,$orth-tier)]][1]
                            /ANNOTATION_VALUE"/>
              <!-- Use orth text if it differs from headword (multi-word utt) -->
              <xsl:variable name="example-src"
                select="if (normalize-space($utterance-orth-text)!=$headword
                            and normalize-space($utterance-orth-text)!='')
                        then $utterance-orth-text
                        else $eg-orth"/>

              <xsl:variable name="eg-trans"
                select="key('ref-by-parent',$eg-parent-id)
                            [ancestor::TIER[starts-with(@TIER_ID,$trans-prefix)]]"/>

              <example>
                <form lang="{$source-lang}">
                  <text><xsl:value-of select="$example-src"/></text>
                </form>
                <xsl:for-each select="$eg-trans">
                  <xsl:variable name="tl"
                    select="if (contains(
                                substring-after(ancestor::TIER/@TIER_ID,$trans-prefix),'@'))
                            then substring-before(
                                   substring-after(ancestor::TIER/@TIER_ID,$trans-prefix),'@')
                            else substring-after(ancestor::TIER/@TIER_ID,$trans-prefix)"/>
                  <xsl:if test="normalize-space(ANNOTATION_VALUE)!=''">
                    <translation type="Frame sentence">
                      <form lang="{$tl}">
                        <text><xsl:value-of select="ANNOTATION_VALUE"/></text>
                      </form>
                    </translation>
                  </xsl:if>
                </xsl:for-each>
              </example>
            </xsl:for-each>

          </sense>

          <!-- Etymology (DMLex etymonUnit JSON → LIFT custom field) -->
          <xsl:if test="normalize-space($etym-json)!=''">
            <xsl:variable name="lang-code"
              select="replace($etym-json,
                        '.*&quot;langCode&quot;\s*:\s*&quot;([^&quot;]+)&quot;.*','$1')"/>
            <xsl:variable name="etymon-text"
              select="replace($etym-json,
                        '.*&quot;text&quot;\s*:\s*&quot;([^&quot;]+)&quot;.*','$1')"/>
            <xsl:variable name="etymon-trans"
              select="replace($etym-json,
                        '.*&quot;translation&quot;\s*:\s*&quot;([^&quot;]+)&quot;.*','$1')"/>
            <xsl:variable name="reconstructed"
              select="contains($etym-json,'&quot;reconstructed&quot;:true')"/>

            <!-- LIFT does not have a native etymology element; use <note type="etym"> -->
            <note type="etym" its:translate="no">
              <xsl:value-of select="concat(
                if ($reconstructed) then '*' else '',
                $etymon-text,
                ' [', $lang-code, ']',
                if (normalize-space($etymon-trans)!=$etym-json)
                  then concat(' &quot;',$etymon-trans,'&quot;')
                  else ''
              )"/>
            </note>
          </xsl:if>

        </entry>
      </xsl:for-each-group>
    </lift>
  </xsl:template>

  <xsl:template match="text()"/>

</xsl:stylesheet>
