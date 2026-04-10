<?xml version="1.0" encoding="UTF-8"?>
<!--
  eaf-to-tmx.xsl
  Extracts bilingual translation units from an ELAN .eaf file
  directly into TMX 1.4b format.

  Each root utterance with both an orthographic transcription AND
  at least one translation tier produces one or more TMX <tu> elements
  (one per translation language).

  IPA, morpheme gloss, etymology, and psychoacoustic tier data are
  preserved as TMX <prop> elements with x-its-no-translate markers,
  following ITS 1.0 conventions.

  Time alignment is stored as:
    <prop type="x-eaf-time-start">0</prop>
    <prop type="x-eaf-time-end">1800</prop>

  This enables WaveSurfer.js or similar players to reconstruct
  time-coded playback from the TMX file without the original EAF.

  Parameters mirror eaf-to-xliff.xsl for pipeline consistency.
-->
<xsl:stylesheet
  xmlns:xsl = "http://www.w3.org/1999/XSL/Transform"
  xmlns:its = "http://www.w3.org/2005/11/its"
  version   = "2.0">

  <xsl:output method="xml" encoding="UTF-8" indent="yes"/>
  <xsl:strip-space elements="*"/>

  <xsl:param name="source-lang"   select="'und'"/>
  <xsl:param name="admin-lang"    select="'en'"/>
  <xsl:param name="trans-prefix"  select="'trans-'"/>
  <xsl:param name="orth-tier"     select="'orth'"/>
  <xsl:param name="ipa-tier"      select="'ipa'"/>
  <xsl:param name="morph-tier"    select="'morph'"/>
  <xsl:param name="gloss-tier"    select="'gloss'"/>
  <xsl:param name="etym-tier"     select="'etym'"/>
  <xsl:param name="psych-tier"    select="'psych'"/>
  <xsl:param name="creationtool"  select="'eaf-to-tmx.xsl'"/>
  <xsl:param name="creationdate"  select="string(current-dateTime())"/>

  <xsl:key name="ts-by-id"       match="TIME_SLOT"      use="@TIME_SLOT_ID"/>
  <xsl:key name="ref-by-parent"  match="ANNOTATION/REF_ANNOTATION" use="@ANNOTATION_REF"/>

  <!-- ============================================================
       Root: ANNOTATION_DOCUMENT → TMX
       ============================================================ -->
  <xsl:template match="/ANNOTATION_DOCUMENT">
    <xsl:variable name="media"
      select="HEADER/MEDIA_DESCRIPTOR[1]/@RELATIVE_MEDIA_URL"/>

    <tmx version="1.4">
      <header
        creationtool        = "{$creationtool}"
        creationtoolversion = "1.0"
        datatype            = "PlainText"
        segtype             = "sentence"
        adminlang           = "{$admin-lang}"
        srclang             = "{$source-lang}"
        creationdate        = "{$creationdate}">

        <note xml:lang="{$admin-lang}">
          EAF source: <xsl:value-of select="$media"/>
        </note>
        <note xml:lang="{$admin-lang}">
          ITS: ipa, gloss, morph, etymology, psychoacoustic tiers are translate="no"
        </note>

        <!-- Media reference prop for WaveSurfer.js integration -->
        <prop type="x-media-url"><xsl:value-of select="$media"/></prop>
        <prop type="x-eaf-format">
          <xsl:value-of select="/ANNOTATION_DOCUMENT/@FORMAT"/>
        </prop>
        <xsl:variable name="olac"
          select="HEADER/PROPERTY[@NAME='OLAC-type']"/>
        <xsl:if test="$olac">
          <prop type="x-olac-type"><xsl:value-of select="$olac"/></prop>
        </xsl:if>
      </header>

      <body>
        <xsl:apply-templates
          select="//TIER[not(@PARENT_REF)]
                        //ANNOTATION/ALIGNABLE_ANNOTATION"/>
      </body>
    </tmx>
  </xsl:template>

  <!-- ============================================================
       Each root ALIGNABLE_ANNOTATION → one or more <tu>
       ============================================================ -->
  <xsl:template match="ALIGNABLE_ANNOTATION">
    <xsl:variable name="ann-id"  select="@ANNOTATION_ID"/>
    <xsl:variable name="ts1"     select="@TIME_SLOT_REF1"/>
    <xsl:variable name="ts2"     select="@TIME_SLOT_REF2"/>
    <xsl:variable name="t-start" select="key('ts-by-id',$ts1)/@TIME_VALUE"/>
    <xsl:variable name="t-end"   select="key('ts-by-id',$ts2)/@TIME_VALUE"/>
    <xsl:variable name="speaker" select="ancestor::TIER/@PARTICIPANT"/>

    <!-- Orth text for this utterance -->
    <xsl:variable name="orth-ann"
      select="key('ref-by-parent',$ann-id)
                  [ancestor::TIER[starts-with(@TIER_ID,$orth-tier)]][1]"/>
    <xsl:variable name="orth-text" select="$orth-ann/ANNOTATION_VALUE"/>
    <xsl:variable name="orth-id"   select="$orth-ann/@ANNOTATION_ID"/>

    <!-- Child tiers of orth -->
    <xsl:variable name="ipa-text"
      select="key('ref-by-parent',$orth-id)
                  [ancestor::TIER[starts-with(@TIER_ID,$ipa-tier)]][1]
                  /ANNOTATION_VALUE"/>
    <xsl:variable name="morph-text"
      select="key('ref-by-parent',$orth-id)
                  [ancestor::TIER[starts-with(@TIER_ID,$morph-tier)]][1]
                  /ANNOTATION_VALUE"/>
    <xsl:variable name="morph-id"
      select="key('ref-by-parent',$orth-id)
                  [ancestor::TIER[starts-with(@TIER_ID,$morph-tier)]][1]
                  /@ANNOTATION_ID"/>
    <xsl:variable name="gloss-text"
      select="key('ref-by-parent',$morph-id)
                  [ancestor::TIER[starts-with(@TIER_ID,$gloss-tier)]][1]
                  /ANNOTATION_VALUE"/>
    <xsl:variable name="etym-text"
      select="key('ref-by-parent',$orth-id)
                  [ancestor::TIER[starts-with(@TIER_ID,$etym-tier)]][1]
                  /ANNOTATION_VALUE"/>
    <xsl:variable name="psych-text"
      select="//TIER[starts-with(@TIER_ID,$psych-tier)]
                //ALIGNABLE_ANNOTATION
                    [@TIME_SLOT_REF1=$ts1 and @TIME_SLOT_REF2=$ts2]
                /ANNOTATION_VALUE"/>

    <!-- One <tu> per translation language found for this utterance -->
    <xsl:for-each
      select="key('ref-by-parent',$ann-id)
                  [ancestor::TIER[starts-with(@TIER_ID,$trans-prefix)]]">

      <xsl:variable name="trans-tier-id"
        select="ancestor::TIER/@TIER_ID"/>
      <xsl:variable name="lang-suffix"
        select="substring-after($trans-tier-id,$trans-prefix)"/>
      <xsl:variable name="trans-lang"
        select="if (contains($lang-suffix,'@'))
                then substring-before($lang-suffix,'@')
                else $lang-suffix"/>
      <xsl:variable name="trans-text" select="ANNOTATION_VALUE"/>

      <xsl:if test="normalize-space($orth-text)!=''
                    and normalize-space($trans-text)!=''">
        <tu tuid        = "{$ann-id}.{$trans-lang}"
            datatype    = "PlainText"
            creationdate= "{$creationdate}">

          <!-- Speaker -->
          <prop type="x-speaker"><xsl:value-of select="$speaker"/></prop>

          <!-- Time alignment — enables WaveSurfer.js region linking -->
          <prop type="x-eaf-time-start"><xsl:value-of select="$t-start"/></prop>
          <prop type="x-eaf-time-end">  <xsl:value-of select="$t-end"/></prop>
          <prop type="x-eaf-ann-id">    <xsl:value-of select="$ann-id"/></prop>

          <!-- ITS translate="no" metalinguistic props -->
          <xsl:if test="normalize-space($ipa-text)!=''">
            <prop type="x-its-no-translate">ipa</prop>
            <prop type="x-ipa"><xsl:value-of select="$ipa-text"/></prop>
          </xsl:if>
          <xsl:if test="normalize-space($morph-text)!=''">
            <prop type="x-its-no-translate">morph</prop>
            <prop type="x-morph"><xsl:value-of select="$morph-text"/></prop>
          </xsl:if>
          <xsl:if test="normalize-space($gloss-text)!=''">
            <prop type="x-its-no-translate">gloss</prop>
            <prop type="x-gloss"><xsl:value-of select="$gloss-text"/></prop>
          </xsl:if>
          <xsl:if test="normalize-space($etym-text)!=''">
            <!-- DMLex etymonUnit JSON blob -->
            <prop type="x-its-no-translate">etymology</prop>
            <prop type="x-etymology"><xsl:value-of select="$etym-text"/></prop>
          </xsl:if>
          <xsl:if test="normalize-space($psych-text)!=''">
            <prop type="x-its-no-translate">psychoacoustic</prop>
            <prop type="x-psychoacoustic"><xsl:value-of select="$psych-text"/></prop>
          </xsl:if>

          <!-- Source TUV: vernacular orthographic form -->
          <tuv xml:lang="{$source-lang}">
            <seg><xsl:value-of select="$orth-text"/></seg>
          </tuv>

          <!-- Target TUV: translation -->
          <tuv xml:lang="{$trans-lang}">
            <seg><xsl:value-of select="$trans-text"/></seg>
          </tuv>

        </tu>
      </xsl:if>
    </xsl:for-each>
  </xsl:template>

  <xsl:template match="text()"/>

</xsl:stylesheet>
