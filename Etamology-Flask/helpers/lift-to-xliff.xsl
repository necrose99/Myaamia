<?xml version="1.0" encoding="UTF-8"?>
<!--
  lift-to-xliff.xsl
  Transforms LIFT 0.13 (Lexicon Interchange FormaT) to XLIFF 1.2
  with ITS 1.0 (Internationalization Tag Set) metadata.

  Direction : LIFT → XLIFF
  Standard refs:
    LIFT   — https://github.com/sillsdev/lift-standard
    XLIFF  — http://docs.oasis-open.org/xliff/xliff-core/xliff-core.html
    ITS    — http://www.w3.org/2005/11/its

  Each LIFT <entry> becomes one XLIFF <file>.
  Each LIFT <sense> becomes one XLIFF <trans-unit> group.
  Lexical-unit / citation form → source text.
  Gloss / definition per target language → target text.
  ITS its:translate="no" is applied to grammatical metadata nodes.
-->
<xsl:stylesheet
  xmlns:xsl  = "http://www.w3.org/1999/XSL/Transform"
  xmlns:its  = "http://www.w3.org/2005/11/its"
  xmlns:lift = "http://www.w3.org/2005/11/its"
  version    = "2.0"
  exclude-result-prefixes="lift">

  <!-- ============================================================
       Parameters
       ============================================================ -->
  <!-- Source language BCP-47 tag (vernacular / object language) -->
  <xsl:param name="source-lang"  select="'und'"/>
  <!-- Target language BCP-47 tag (analysis / gloss language)    -->
  <xsl:param name="target-lang"  select="'en'"/>
  <!-- Tool name written into XLIFF header                        -->
  <xsl:param name="tool-name"    select="'lift-to-xliff.xsl'"/>
  <!-- XLIFF datatype attribute value                             -->
  <xsl:param name="datatype"     select="'lift'"/>

  <!-- ============================================================
       Output declaration
       ============================================================ -->
  <xsl:output method="xml" encoding="UTF-8" indent="yes"/>
  <xsl:strip-space elements="*"/>

  <!-- ============================================================
       Root template — LIFT <lift> element
       ============================================================ -->
  <xsl:template match="/lift">
    <xliff version="1.2"
           xmlns="urn:oasis:names:tc:xliff:document:1.2"
           xmlns:its="http://www.w3.org/2005/11/its"
           its:version="1.0">

      <!--
        ITS rules block embedded in XLIFF header.
        • <head> and <code> children must not be translated.
        • <source> carries the translatable text.
        • grammatical-info content is metadata, not translatable.
      -->
      <its:rules version="1.0">
        <its:translateRule selector="//note[@type='grammatical-info']"
                           translate="no"/>
        <its:translateRule selector="//note[@type='semantic-domain']"
                           translate="no"/>
        <its:withinTextRule selector="//ph" withinText="yes"/>
        <its:withinTextRule selector="//g"  withinText="yes"/>
      </its:rules>

      <!-- One XLIFF <file> per LIFT <entry> -->
      <xsl:apply-templates select="entry"/>
    </xliff>
  </xsl:template>

  <!-- ============================================================
       LIFT <entry>  →  XLIFF <file>
       ============================================================ -->
  <xsl:template match="entry"
                xmlns="urn:oasis:names:tc:xliff:document:1.2">

    <xsl:variable name="entry-id"
                  select="if (@id) then @id else generate-id()"/>
    <xsl:variable name="headword"
                  select="(lexical-unit/form[@lang=$source-lang]/text/text()
                           | citation/form[@lang=$source-lang]/text/text())[1]"/>

    <file original  = "{$entry-id}"
          source-language = "{$source-lang}"
          target-language = "{$target-lang}"
          datatype  = "{$datatype}"
          its:version="1.0"
          xmlns:its = "http://www.w3.org/2005/11/its">

      <header>
        <tool tool-id="lift-to-xliff" tool-name="{$tool-name}"/>
        <!-- Carry LIFT date-deleted / date-created as notes -->
        <xsl:if test="@dateCreated">
          <note>LIFT dateCreated: <xsl:value-of select="@dateCreated"/></note>
        </xsl:if>
        <xsl:if test="@dateModified">
          <note>LIFT dateModified: <xsl:value-of select="@dateModified"/></note>
        </xsl:if>
        <!-- Morphological type — ITS marks this non-translatable -->
        <xsl:if test="@morph-type">
          <note its:translate="no">morph-type: <xsl:value-of select="@morph-type"/></note>
        </xsl:if>
        <!-- Lexical relations -->
        <xsl:for-each select="relation">
          <note its:translate="no">relation type="<xsl:value-of select="@type"/>" ref="<xsl:value-of select="@ref"/>"</note>
        </xsl:for-each>
      </header>

      <body>
        <!-- Lexical-unit headword as a standalone trans-unit -->
        <xsl:if test="lexical-unit/form[@lang=$source-lang]">
          <trans-unit id="{$entry-id}.headword" resname="lexical-unit">
            <source xml:lang="{$source-lang}">
              <xsl:value-of
                select="lexical-unit/form[@lang=$source-lang]/text"/>
            </source>
            <!-- If a citation form differs, add as alt-trans -->
            <xsl:if test="citation/form[@lang=$source-lang]
                          and citation/form[@lang=$source-lang]/text
                              != lexical-unit/form[@lang=$source-lang]/text">
              <alt-trans origin="citation-form" match-quality="100">
                <source xml:lang="{$source-lang}">
                  <xsl:value-of
                    select="citation/form[@lang=$source-lang]/text"/>
                </source>
              </alt-trans>
            </xsl:if>
          </trans-unit>
        </xsl:if>

        <!-- One trans-unit group per sense -->
        <xsl:apply-templates select="sense">
          <xsl:with-param name="entry-id" select="$entry-id"/>
        </xsl:apply-templates>

        <!-- Pronunciation notes — non-translatable phonetic data -->
        <xsl:for-each select="pronunciation/form">
          <trans-unit id="{$entry-id}.pron.{position()}"
                      resname="pronunciation"
                      its:translate="no"
                      xmlns:its="http://www.w3.org/2005/11/its">
            <source xml:lang="{@lang}">
              <xsl:value-of select="text"/>
            </source>
          </trans-unit>
        </xsl:for-each>
      </body>
    </file>
  </xsl:template>

  <!-- ============================================================
       LIFT <sense>  →  XLIFF <group> of <trans-unit> elements
       ============================================================ -->
  <xsl:template match="sense"
                xmlns="urn:oasis:names:tc:xliff:document:1.2">
    <xsl:param name="entry-id"/>

    <xsl:variable name="sense-id"
                  select="if (@id) then @id
                          else concat($entry-id,'.sense.',position())"/>

    <group id="{$sense-id}" restype="sense">

      <!-- Grammatical information — ITS: do not translate -->
      <xsl:if test="grammatical-info">
        <note its:translate="no"
              xmlns:its="http://www.w3.org/2005/11/its">
          grammatical-info value="<xsl:value-of
            select="grammatical-info/@value"/>"
        </note>
      </xsl:if>

      <!-- Semantic domains — ITS: do not translate -->
      <xsl:for-each select="semantic-domain">
        <note its:translate="no"
              xmlns:its="http://www.w3.org/2005/11/its">
          semantic-domain: <xsl:value-of select="@name"/>
        </note>
      </xsl:for-each>

      <!-- Gloss per analysis language → trans-unit (source = headword context) -->
      <xsl:for-each select="gloss">
        <xsl:variable name="gloss-lang" select="@lang"/>
        <trans-unit id="{$sense-id}.gloss.{$gloss-lang}"
                    resname="gloss">
          <source xml:lang="{$source-lang}">
            <xsl:value-of
              select="../../lexical-unit/form[@lang=$source-lang]/text"/>
          </source>
          <target xml:lang="{$gloss-lang}">
            <xsl:value-of select="text"/>
          </target>
        </trans-unit>
      </xsl:for-each>

      <!-- Definition (richer than gloss) -->
      <xsl:for-each select="definition/form">
        <xsl:variable name="def-lang" select="@lang"/>
        <trans-unit id="{$sense-id}.definition.{$def-lang}"
                    resname="definition">
          <source xml:lang="{$source-lang}">
            <xsl:value-of
              select="../../../../lexical-unit/form[@lang=$source-lang]/text"/>
          </source>
          <target xml:lang="{$def-lang}">
            <xsl:value-of select="text"/>
          </target>
          <note>definition</note>
        </trans-unit>
      </xsl:for-each>

      <!-- Examples -->
      <xsl:for-each select="example">
        <xsl:variable name="ex-pos" select="position()"/>
        <xsl:for-each select="form[@lang=$source-lang]">
          <trans-unit id="{$sense-id}.example.{$ex-pos}"
                      resname="example">
            <source xml:lang="{@lang}">
              <xsl:value-of select="text"/>
            </source>
            <!-- Translated example sentence -->
            <xsl:for-each
              select="../../translation/form[@lang=$target-lang]">
              <target xml:lang="{@lang}">
                <xsl:value-of select="text"/>
              </target>
            </xsl:for-each>
          </trans-unit>
        </xsl:for-each>
      </xsl:for-each>

    </group>
  </xsl:template>

  <!-- ============================================================
       Suppress unmatched LIFT nodes silently
       ============================================================ -->
  <xsl:template match="text()"/>

</xsl:stylesheet>
