<?xml version="1.0" encoding="UTF-8"?>
<!--
  tmx-to-eaf.xsl
  Reconstructs an ELAN Annotation Format (EAF v3.0) document from a
  TMX 1.4b file that was produced by eaf-to-tmx.xsl.

  Recovered structure:
    • x-eaf-time-start / x-eaf-time-end props → TIME_ORDER / TIME_SLOT elements
    • srclang TUV/seg → orth@SP1 tier (Symbolic_Subdivision of ref)
    • Each target-language TUV → trans-{lang}@SP1 tier (Symbolic_Association)
    • x-ipa prop → ipa@SP1 tier
    • x-morph prop → morph@SP1 tier
    • x-gloss prop → gloss@SP1 tier
    • x-etymology prop → etym@SP1 tier
    • x-psychoacoustic prop → psych@SP1 tier (time-alignable)
    • x-media-url header prop → MEDIA_DESCRIPTOR

  Limitations:
    • All annotations reconstructed as single-speaker (SP1)
    • Time slots are re-generated from x-eaf-time-* props
    • Annotation IDs are regenerated (not original)
    • LINGUISTIC_TYPE and CONSTRAINT boilerplate is standard
-->
<xsl:stylesheet
  xmlns:xsl = "http://www.w3.org/1999/XSL/Transform"
  version   = "2.0">

  <xsl:output method="xml" encoding="UTF-8" indent="yes"/>
  <xsl:strip-space elements="*"/>

  <xsl:param name="speaker"     select="'SP1'"/>
  <xsl:param name="eaf-version" select="'3.0'"/>
  <xsl:param name="author"      select="'tmx-to-eaf.xsl'"/>

  <!-- ============================================================
       Root: TMX → ANNOTATION_DOCUMENT
       ============================================================ -->
  <xsl:template match="/tmx">
    <xsl:variable name="src-lang"   select="header/@srclang"/>
    <xsl:variable name="media-url"  select="(header/prop[@type='x-media-url'],'')[1]"/>
    <xsl:variable name="tus"        select="body/tu"/>

    <!-- Deduplicate time intervals to generate TIME_SLOTs -->
    <xsl:variable name="intervals">
      <xsl:for-each-group select="$tus"
                          group-by="concat(prop[@type='x-eaf-time-start'],
                                          '_',
                                          prop[@type='x-eaf-time-end'])">
        <interval start="{prop[@type='x-eaf-time-start']}"
                  end  ="{prop[@type='x-eaf-time-end']}"
                  pos  ="{position()}"/>
      </xsl:for-each-group>
    </xsl:variable>

    <!-- Collect all unique target languages -->
    <xsl:variable name="tgt-langs"
      select="distinct-values($tus/tuv[not(@xml:lang=$src-lang)]/@xml:lang)"/>

    <!-- Determine if we have IPA / morph / gloss / etym / psych data -->
    <xsl:variable name="has-ipa"   select="exists($tus/prop[@type='x-ipa'])"/>
    <xsl:variable name="has-morph" select="exists($tus/prop[@type='x-morph'])"/>
    <xsl:variable name="has-gloss" select="exists($tus/prop[@type='x-gloss'])"/>
    <xsl:variable name="has-etym"  select="exists($tus/prop[@type='x-etymology'])"/>
    <xsl:variable name="has-psych" select="exists($tus/prop[@type='x-psychoacoustic'])"/>

    <ANNOTATION_DOCUMENT
      AUTHOR   = "{$author}"
      DATE     = "{current-dateTime()}"
      FORMAT   = "{$eaf-version}"
      VERSION  = "{$eaf-version}"
      xmlns:xsi= "http://www.w3.org/2001/XMLSchema-instance"
      xsi:noNamespaceSchemaLocation=
        "http://www.mpi.nl/tools/elan/EAFv3.0.xsd">

      <HEADER MEDIA_FILE="" TIME_UNITS="milliseconds">
        <xsl:if test="normalize-space($media-url)!=''">
          <MEDIA_DESCRIPTOR
            MEDIA_URL="{$media-url}"
            MIME_TYPE="audio/x-wav"
            RELATIVE_MEDIA_URL="{tokenize($media-url,'/')[last()]}"/>
        </xsl:if>
        <PROPERTY NAME="URN">
          urn:nl-mpi-tools-elan-eaf:tmx-reconstructed-<xsl:value-of
            select="format-dateTime(current-dateTime(),'[Y][M01][D01]')"/>
        </PROPERTY>
        <PROPERTY NAME="lastUsedAnnotationId">
          <xsl:value-of select="count($tus) * 10"/>
        </PROPERTY>
        <xsl:if test="header/prop[@type='x-olac-type']">
          <PROPERTY NAME="OLAC-type">
            <xsl:value-of select="header/prop[@type='x-olac-type']"/>
          </PROPERTY>
        </xsl:if>
      </HEADER>

      <!-- TIME_ORDER: one pair of slots per unique interval -->
      <TIME_ORDER>
        <xsl:for-each select="$intervals/interval">
          <TIME_SLOT TIME_SLOT_ID="ts{(@pos*2)-1}"
                     TIME_VALUE="{@start}"/>
          <TIME_SLOT TIME_SLOT_ID="ts{@pos*2}"
                     TIME_VALUE="{@end}"/>
        </xsl:for-each>
      </TIME_ORDER>

      <!-- REF tier (utterance numbers, root time-alignable) -->
      <TIER LINGUISTIC_TYPE_REF="ref-type"
            PARTICIPANT="{$speaker}"
            TIER_ID="ref@{$speaker}">
        <xsl:for-each select="$intervals/interval">
          <xsl:variable name="pos" select="@pos"/>
          <xsl:variable name="start" select="@start"/>
          <ANNOTATION>
            <ALIGNABLE_ANNOTATION
              ANNOTATION_ID="a{($pos*10)-9}"
              TIME_SLOT_REF1="ts{($pos*2)-1}"
              TIME_SLOT_REF2="ts{$pos*2}">
              <ANNOTATION_VALUE>U<xsl:value-of select="$pos"/></ANNOTATION_VALUE>
            </ALIGNABLE_ANNOTATION>
          </ANNOTATION>
        </xsl:for-each>
      </TIER>

      <!-- ORTH tier: vernacular text from source TUV -->
      <TIER LINGUISTIC_TYPE_REF="orth-type"
            PARENT_REF="ref@{$speaker}"
            PARTICIPANT="{$speaker}"
            TIER_ID="orth@{$speaker}">
        <xsl:for-each-group select="$tus"
                            group-by="concat(prop[@type='x-eaf-time-start'],
                                            '_',
                                            prop[@type='x-eaf-time-end'])">
          <xsl:variable name="tu"    select="current-group()[1]"/>
          <xsl:variable name="pos"   select="position()"/>
          <xsl:variable name="src"   select="$tu/tuv[@xml:lang=$src-lang]/seg"/>
          <ANNOTATION>
            <REF_ANNOTATION
              ANNOTATION_ID  = "a{($pos*10)-8}"
              ANNOTATION_REF = "a{($pos*10)-9}">
              <ANNOTATION_VALUE><xsl:value-of select="$src"/></ANNOTATION_VALUE>
            </REF_ANNOTATION>
          </ANNOTATION>
        </xsl:for-each-group>
      </TIER>

      <!-- IPA TIER -->
      <xsl:if test="$has-ipa">
        <TIER LINGUISTIC_TYPE_REF="ipa-type"
              PARENT_REF="orth@{$speaker}"
              PARTICIPANT="{$speaker}"
              TIER_ID="ipa@{$speaker}">
          <xsl:for-each-group select="$tus[prop[@type='x-ipa']]"
                              group-by="concat(prop[@type='x-eaf-time-start'],
                                              '_',
                                              prop[@type='x-eaf-time-end'])">
            <xsl:variable name="pos"  select="position()"/>
            <xsl:variable name="tu"   select="current-group()[1]"/>
            <ANNOTATION>
              <REF_ANNOTATION
                ANNOTATION_ID  = "a{($pos*10)-7}"
                ANNOTATION_REF = "a{($pos*10)-8}">
                <ANNOTATION_VALUE>
                  <xsl:value-of select="$tu/prop[@type='x-ipa']"/>
                </ANNOTATION_VALUE>
              </REF_ANNOTATION>
            </ANNOTATION>
          </xsl:for-each-group>
        </TIER>
      </xsl:if>

      <!-- MORPH TIER -->
      <xsl:if test="$has-morph">
        <TIER LINGUISTIC_TYPE_REF="morph-type"
              PARENT_REF="orth@{$speaker}"
              PARTICIPANT="{$speaker}"
              TIER_ID="morph@{$speaker}">
          <xsl:for-each-group select="$tus[prop[@type='x-morph']]"
                              group-by="concat(prop[@type='x-eaf-time-start'],
                                              '_',
                                              prop[@type='x-eaf-time-end'])">
            <xsl:variable name="pos" select="position()"/>
            <xsl:variable name="tu"  select="current-group()[1]"/>
            <ANNOTATION>
              <REF_ANNOTATION
                ANNOTATION_ID  = "a{($pos*10)-6}"
                ANNOTATION_REF = "a{($pos*10)-8}">
                <ANNOTATION_VALUE>
                  <xsl:value-of select="$tu/prop[@type='x-morph']"/>
                </ANNOTATION_VALUE>
              </REF_ANNOTATION>
            </ANNOTATION>
          </xsl:for-each-group>
        </TIER>
      </xsl:if>

      <!-- GLOSS TIER (child of morph) -->
      <xsl:if test="$has-gloss">
        <TIER LINGUISTIC_TYPE_REF="gloss-type"
              PARENT_REF="morph@{$speaker}"
              PARTICIPANT="{$speaker}"
              TIER_ID="gloss@{$speaker}">
          <xsl:for-each-group select="$tus[prop[@type='x-gloss']]"
                              group-by="concat(prop[@type='x-eaf-time-start'],
                                              '_',
                                              prop[@type='x-eaf-time-end'])">
            <xsl:variable name="pos" select="position()"/>
            <xsl:variable name="tu"  select="current-group()[1]"/>
            <ANNOTATION>
              <REF_ANNOTATION
                ANNOTATION_ID  = "a{($pos*10)-5}"
                ANNOTATION_REF = "a{($pos*10)-6}">
                <ANNOTATION_VALUE>
                  <xsl:value-of select="$tu/prop[@type='x-gloss']"/>
                </ANNOTATION_VALUE>
              </REF_ANNOTATION>
            </ANNOTATION>
          </xsl:for-each-group>
        </TIER>
      </xsl:if>

      <!-- TRANSLATION TIERS — one per target language -->
      <xsl:for-each select="$tgt-langs">
        <xsl:variable name="lang" select="."/>
        <TIER LINGUISTIC_TYPE_REF="trans-type"
              PARENT_REF="ref@{$speaker}"
              PARTICIPANT="{$speaker}"
              TIER_ID="trans-{$lang}@{$speaker}">
          <xsl:for-each-group
            select="$tus[tuv[@xml:lang=$lang]]"
            group-by="concat(prop[@type='x-eaf-time-start'],
                            '_',
                            prop[@type='x-eaf-time-end'])">
            <xsl:variable name="pos" select="position()"/>
            <xsl:variable name="tu"  select="current-group()[1]"/>
            <ANNOTATION>
              <REF_ANNOTATION
                ANNOTATION_ID  = "a{($pos*10)-4}{translate($lang,'-','')}r"
                ANNOTATION_REF = "a{($pos*10)-9}">
                <ANNOTATION_VALUE>
                  <xsl:value-of select="$tu/tuv[@xml:lang=$lang]/seg"/>
                </ANNOTATION_VALUE>
              </REF_ANNOTATION>
            </ANNOTATION>
          </xsl:for-each-group>
        </TIER>
      </xsl:for-each>

      <!-- ETYMOLOGY TIER -->
      <xsl:if test="$has-etym">
        <TIER LINGUISTIC_TYPE_REF="etym-type"
              PARENT_REF="orth@{$speaker}"
              PARTICIPANT="{$speaker}"
              TIER_ID="etym@{$speaker}">
          <xsl:for-each-group select="$tus[prop[@type='x-etymology']]"
                              group-by="concat(prop[@type='x-eaf-time-start'],
                                              '_',
                                              prop[@type='x-eaf-time-end'])">
            <xsl:variable name="pos" select="position()"/>
            <xsl:variable name="tu"  select="current-group()[1]"/>
            <ANNOTATION>
              <REF_ANNOTATION
                ANNOTATION_ID  = "a{($pos*10)-3}"
                ANNOTATION_REF = "a{($pos*10)-8}">
                <ANNOTATION_VALUE>
                  <xsl:value-of select="$tu/prop[@type='x-etymology']"/>
                </ANNOTATION_VALUE>
              </REF_ANNOTATION>
            </ANNOTATION>
          </xsl:for-each-group>
        </TIER>
      </xsl:if>

      <!-- PSYCHOACOUSTIC TIER (time-alignable, independent root) -->
      <xsl:if test="$has-psych">
        <TIER LINGUISTIC_TYPE_REF="note-type"
              PARTICIPANT="{$speaker}"
              TIER_ID="psych@{$speaker}">
          <xsl:for-each-group select="$tus[prop[@type='x-psychoacoustic']]"
                              group-by="concat(prop[@type='x-eaf-time-start'],
                                              '_',
                                              prop[@type='x-eaf-time-end'])">
            <xsl:variable name="pos"   select="position()"/>
            <xsl:variable name="tu"    select="current-group()[1]"/>
            <ANNOTATION>
              <ALIGNABLE_ANNOTATION
                ANNOTATION_ID  = "ap{$pos}"
                TIME_SLOT_REF1 = "ts{($pos*2)-1}"
                TIME_SLOT_REF2 = "ts{$pos*2}">
                <ANNOTATION_VALUE>
                  <xsl:value-of select="$tu/prop[@type='x-psychoacoustic']"/>
                </ANNOTATION_VALUE>
              </ALIGNABLE_ANNOTATION>
            </ANNOTATION>
          </xsl:for-each-group>
        </TIER>
      </xsl:if>

      <!-- LINGUISTIC TYPES -->
      <LINGUISTIC_TYPE GRAPHIC_REFERENCES="false"
                       LINGUISTIC_TYPE_ID="ref-type"
                       TIME_ALIGNABLE="true"/>
      <LINGUISTIC_TYPE CONSTRAINTS="Symbolic_Subdivision"
                       GRAPHIC_REFERENCES="false"
                       LINGUISTIC_TYPE_ID="orth-type"
                       TIME_ALIGNABLE="false"/>
      <LINGUISTIC_TYPE CONSTRAINTS="Symbolic_Association"
                       GRAPHIC_REFERENCES="false"
                       LINGUISTIC_TYPE_ID="ipa-type"
                       TIME_ALIGNABLE="false"/>
      <LINGUISTIC_TYPE CONSTRAINTS="Symbolic_Subdivision"
                       GRAPHIC_REFERENCES="false"
                       LINGUISTIC_TYPE_ID="morph-type"
                       TIME_ALIGNABLE="false"/>
      <LINGUISTIC_TYPE CONSTRAINTS="Symbolic_Subdivision"
                       GRAPHIC_REFERENCES="false"
                       LINGUISTIC_TYPE_ID="gloss-type"
                       TIME_ALIGNABLE="false"/>
      <LINGUISTIC_TYPE CONSTRAINTS="Symbolic_Association"
                       GRAPHIC_REFERENCES="false"
                       LINGUISTIC_TYPE_ID="trans-type"
                       TIME_ALIGNABLE="false"/>
      <LINGUISTIC_TYPE CONSTRAINTS="Symbolic_Association"
                       GRAPHIC_REFERENCES="false"
                       LINGUISTIC_TYPE_ID="etym-type"
                       TIME_ALIGNABLE="false"/>
      <LINGUISTIC_TYPE GRAPHIC_REFERENCES="false"
                       LINGUISTIC_TYPE_ID="note-type"
                       TIME_ALIGNABLE="true"/>

      <!-- CONSTRAINTS -->
      <CONSTRAINT DESCRIPTION="Symbolic subdivision of a parent annotation"
                  STEREOTYPE="Symbolic_Subdivision"/>
      <CONSTRAINT DESCRIPTION="1-1 association with a parent annotation"
                  STEREOTYPE="Symbolic_Association"/>
      <CONSTRAINT DESCRIPTION="Time alignable annotations within the parent annotation's time interval, gaps are allowed"
                  STEREOTYPE="Included_In"/>

    </ANNOTATION_DOCUMENT>
  </xsl:template>

  <xsl:template match="text()"/>

</xsl:stylesheet>
