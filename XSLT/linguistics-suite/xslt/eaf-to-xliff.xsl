<?xml version="1.0" encoding="UTF-8"?>
<!--
  eaf-to-xliff.xsl
  Transforms an ELAN Annotation Format (EAF / .eaf) document to XLIFF 1.2.

  Mapping strategy:
    • Each ALIGNABLE root annotation (utterance) → one XLIFF <file>
    • Orthographic text (orth tier) → <source>
    • Free translation per language (trans-* tier) → <target>
    • IPA tier values → <note its:translate="no">
    • Morpheme gloss tier → <note its:translate="no">
    • Etymology tier JSON → <note its:translate="no">
    • Psychoacoustic tier → <prop type="x-psychoacoustic"> in <file><header>
    • Time intervals → <context-group> with millisecond values
    • OLAC type property → XLIFF <file @datatype>

  ITS 1.0:
    • Metalinguistic tiers (IPA, gloss, etymology, psychoacoustic)
      carry its:translate="no" throughout.
    • An <its:rules> block in the XLIFF root governs processor behaviour.

  Parameters:
    source-lang   BCP-47 tag for the vernacular (default: "und")
    target-lang   BCP-47 tag for the primary translation tier (default: "en")
    orth-tier     Tier ID prefix for orthography (default: "orth")
    ipa-tier      Tier ID prefix for IPA (default: "ipa")
    morph-tier    Tier ID prefix for morpheme segmentation (default: "morph")
    gloss-tier    Tier ID prefix for interlinear gloss (default: "gloss")
    trans-prefix  Tier ID prefix for translation tiers (default: "trans-")
    etym-tier     Tier ID prefix for etymology (default: "etym")
    psych-tier    Tier ID prefix for psychoacoustics (default: "psych")
-->
<xsl:stylesheet
  xmlns:xsl  = "http://www.w3.org/1999/XSL/Transform"
  xmlns:its  = "http://www.w3.org/2005/11/its"
  version    = "2.0">

  <xsl:output method="xml" encoding="UTF-8" indent="yes"/>
  <xsl:strip-space elements="*"/>

  <!-- ============================================================ Parameters -->
  <xsl:param name="source-lang"   select="'und'"/>
  <xsl:param name="target-lang"   select="'en'"/>
  <xsl:param name="orth-tier"     select="'orth'"/>
  <xsl:param name="ipa-tier"      select="'ipa'"/>
  <xsl:param name="morph-tier"    select="'morph'"/>
  <xsl:param name="gloss-tier"    select="'gloss'"/>
  <xsl:param name="trans-prefix"  select="'trans-'"/>
  <xsl:param name="etym-tier"     select="'etym'"/>
  <xsl:param name="psych-tier"    select="'psych'"/>
  <xsl:param name="tool-name"     select="'eaf-to-xliff.xsl'"/>

  <!-- ============================================================
       Key: annotation id → annotation value (cross-tier lookup)
       ============================================================ -->
  <xsl:key name="ann-by-id"
           match="ANNOTATION/*"
           use="@ANNOTATION_ID"/>

  <!-- Key: tier by id -->
  <xsl:key name="tier-by-id"
           match="TIER"
           use="@TIER_ID"/>

  <!-- Key: child annotations by parent ref -->
  <xsl:key name="ref-by-parent"
           match="ANNOTATION/REF_ANNOTATION"
           use="@ANNOTATION_REF"/>

  <!-- Key: timeslots -->
  <xsl:key name="ts-by-id"
           match="TIME_SLOT"
           use="@TIME_SLOT_ID"/>

  <!-- ============================================================
       Root: ANNOTATION_DOCUMENT → XLIFF
       ============================================================ -->
  <xsl:template match="/ANNOTATION_DOCUMENT">
    <xliff version="1.2"
           xmlns     = "urn:oasis:names:tc:xliff:document:1.2"
           xmlns:its = "http://www.w3.org/2005/11/its"
           its:version="1.0">

      <!-- ITS rules: metalinguistic tiers are not for translation -->
      <its:rules version="1.0">
        <its:translateRule selector="//note[@type='ipa']"         translate="no"/>
        <its:translateRule selector="//note[@type='gloss']"       translate="no"/>
        <its:translateRule selector="//note[@type='morph']"       translate="no"/>
        <its:translateRule selector="//note[@type='etymology']"   translate="no"/>
        <its:translateRule selector="//note[@type='psychoacoustic']" translate="no"/>
        <its:withinTextRule selector="//ph" withinText="yes"/>
      </its:rules>

      <!-- One XLIFF <file> per root (time-alignable) utterance -->
      <xsl:apply-templates
        select="//TIER[not(@PARENT_REF)]
                      //ANNOTATION/ALIGNABLE_ANNOTATION"/>
    </xliff>
  </xsl:template>

  <!-- ============================================================
       ALIGNABLE_ANNOTATION (root utterance) → XLIFF <file>
       ============================================================ -->
  <xsl:template match="ALIGNABLE_ANNOTATION"
                xmlns="urn:oasis:names:tc:xliff:document:1.2">

    <xsl:variable name="ann-id"    select="@ANNOTATION_ID"/>
    <xsl:variable name="ts1"       select="@TIME_SLOT_REF1"/>
    <xsl:variable name="ts2"       select="@TIME_SLOT_REF2"/>
    <xsl:variable name="t-start"   select="key('ts-by-id',$ts1)/@TIME_VALUE"/>
    <xsl:variable name="t-end"     select="key('ts-by-id',$ts2)/@TIME_VALUE"/>
    <xsl:variable name="utt-id"    select="ANNOTATION_VALUE"/>
    <xsl:variable name="tier-id"   select="ancestor::TIER/@TIER_ID"/>
    <xsl:variable name="speaker"   select="ancestor::TIER/@PARTICIPANT"/>

    <!-- Find matching orth annotation (child REF_ANNOTATION of this ann) -->
    <xsl:variable name="orth-ann"
      select="key('ref-by-parent', $ann-id)
                  [ancestor::TIER[starts-with(@TIER_ID,$orth-tier)]][1]"/>
    <xsl:variable name="orth-text"
      select="$orth-ann/ANNOTATION_VALUE"/>

    <!-- IPA annotation (grandchild via orth) -->
    <xsl:variable name="ipa-text"
      select="key('ref-by-parent', $orth-ann/@ANNOTATION_ID)
                  [ancestor::TIER[starts-with(@TIER_ID,$ipa-tier)]][1]
                  /ANNOTATION_VALUE"/>

    <!-- Morph annotation -->
    <xsl:variable name="morph-text"
      select="key('ref-by-parent', $orth-ann/@ANNOTATION_ID)
                  [ancestor::TIER[starts-with(@TIER_ID,$morph-tier)]][1]
                  /ANNOTATION_VALUE"/>

    <!-- Gloss annotation (grandchild via morph) -->
    <xsl:variable name="morph-ann-id"
      select="key('ref-by-parent', $orth-ann/@ANNOTATION_ID)
                  [ancestor::TIER[starts-with(@TIER_ID,$morph-tier)]][1]
                  /@ANNOTATION_ID"/>
    <xsl:variable name="gloss-text"
      select="key('ref-by-parent', $morph-ann-id)
                  [ancestor::TIER[starts-with(@TIER_ID,$gloss-tier)]][1]
                  /ANNOTATION_VALUE"/>

    <!-- Etymology annotation -->
    <xsl:variable name="etym-text"
      select="key('ref-by-parent', $orth-ann/@ANNOTATION_ID)
                  [ancestor::TIER[starts-with(@TIER_ID,$etym-tier)]][1]
                  /ANNOTATION_VALUE"/>

    <!-- Psychoacoustic annotation at same time range -->
    <xsl:variable name="psych-text"
      select="//TIER[starts-with(@TIER_ID,$psych-tier)]
                //ALIGNABLE_ANNOTATION
                    [@TIME_SLOT_REF1=$ts1]
                    [@TIME_SLOT_REF2=$ts2]
                /ANNOTATION_VALUE"/>

    <file original   = "{concat($tier-id,'.',$ann-id)}"
          source-language = "{$source-lang}"
          target-language = "{$target-lang}"
          datatype    = "eaf"
          its:version = "1.0"
          xmlns:its   = "http://www.w3.org/2005/11/its">

      <header>
        <tool tool-id="eaf-to-xliff" tool-name="{$tool-name}"/>
        <!-- Time alignment metadata -->
        <note>EAF utterance-id: <xsl:value-of select="$utt-id"/></note>
        <note>speaker: <xsl:value-of select="$speaker"/></note>
        <note its:translate="no">time-start-ms: <xsl:value-of select="$t-start"/></note>
        <note its:translate="no">time-end-ms: <xsl:value-of select="$t-end"/></note>
        <!-- Psychoacoustic data: ITS translate="no" -->
        <xsl:if test="normalize-space($psych-text)!=''">
          <note type="psychoacoustic"
                its:translate="no">
            <xsl:value-of select="$psych-text"/>
          </note>
        </xsl:if>
        <!-- OLAC type from EAF PROPERTY -->
        <xsl:variable name="olac"
          select="/ANNOTATION_DOCUMENT/HEADER/PROPERTY[@NAME='OLAC-type']"/>
        <xsl:if test="$olac">
          <note its:translate="no">OLAC-type: <xsl:value-of select="$olac"/></note>
        </xsl:if>
      </header>

      <body>
        <!-- Utterance-level trans-unit: source = orth, target = primary translation -->
        <trans-unit id="{$ann-id}.utt" resname="utterance">
          <source xml:lang="{$source-lang}">
            <xsl:choose>
              <xsl:when test="normalize-space($orth-text)!=''">
                <xsl:value-of select="$orth-text"/>
              </xsl:when>
              <xsl:otherwise>
                <xsl:value-of select="ANNOTATION_VALUE"/>
              </xsl:otherwise>
            </xsl:choose>
          </source>

          <!-- Primary target: trans-{target-lang} tier -->
          <xsl:variable name="primary-trans"
            select="key('ref-by-parent', $ann-id)
                        [ancestor::TIER[starts-with(@TIER_ID,
                          concat($trans-prefix,$target-lang))]][1]
                        /ANNOTATION_VALUE"/>
          <xsl:if test="normalize-space($primary-trans)!=''">
            <target xml:lang="{$target-lang}">
              <xsl:value-of select="$primary-trans"/>
            </target>
          </xsl:if>

          <!-- IPA: its:translate="no" -->
          <xsl:if test="normalize-space($ipa-text)!=''">
            <note type="ipa" its:translate="no">
              <xsl:value-of select="$ipa-text"/>
            </note>
          </xsl:if>

          <!-- Morpheme segmentation -->
          <xsl:if test="normalize-space($morph-text)!=''">
            <note type="morph" its:translate="no">
              <xsl:value-of select="$morph-text"/>
            </note>
          </xsl:if>

          <!-- Interlinear gloss -->
          <xsl:if test="normalize-space($gloss-text)!=''">
            <note type="gloss" its:translate="no">
              <xsl:value-of select="$gloss-text"/>
            </note>
          </xsl:if>

          <!-- Etymology (DMLex etymonUnit JSON encoding) -->
          <xsl:if test="normalize-space($etym-text)!=''">
            <note type="etymology" its:translate="no">
              <xsl:value-of select="$etym-text"/>
            </note>
          </xsl:if>

          <!-- Context group: timestamps as XLIFF context -->
          <context-group name="time-alignment" purpose="location">
            <context context-type="x-eaf-time-start">
              <xsl:value-of select="$t-start"/>
            </context>
            <context context-type="x-eaf-time-end">
              <xsl:value-of select="$t-end"/>
            </context>
          </context-group>

        </trans-unit>

        <!-- Alt-trans: additional translation languages -->
        <xsl:for-each
          select="key('ref-by-parent', $ann-id)
                      [ancestor::TIER[starts-with(@TIER_ID,$trans-prefix)]]
                      [not(ancestor::TIER[starts-with(@TIER_ID,
                           concat($trans-prefix,$target-lang,'@'))])
                       and not(ancestor::TIER[@TIER_ID=concat($trans-prefix,$target-lang)])]">
          <xsl:variable name="alt-lang"
            select="substring-after(ancestor::TIER/@TIER_ID, $trans-prefix)"/>
          <!-- strip @SP1 speaker suffix -->
          <xsl:variable name="clean-lang"
            select="if (contains($alt-lang,'@'))
                    then substring-before($alt-lang,'@')
                    else $alt-lang"/>
          <xsl:if test="normalize-space(ANNOTATION_VALUE)!=''">
            <trans-unit id="{$ann-id}.trans.{$clean-lang}"
                        resname="translation">
              <source xml:lang="{$source-lang}">
                <xsl:choose>
                  <xsl:when test="normalize-space($orth-text)!=''">
                    <xsl:value-of select="$orth-text"/>
                  </xsl:when>
                  <xsl:otherwise>
                    <xsl:value-of select="ancestor::ANNOTATION/ALIGNABLE_ANNOTATION/ANNOTATION_VALUE"/>
                  </xsl:otherwise>
                </xsl:choose>
              </source>
              <target xml:lang="{$clean-lang}">
                <xsl:value-of select="ANNOTATION_VALUE"/>
              </target>
            </trans-unit>
          </xsl:if>
        </xsl:for-each>

      </body>
    </file>
  </xsl:template>

  <xsl:template match="text()"/>

</xsl:stylesheet>
