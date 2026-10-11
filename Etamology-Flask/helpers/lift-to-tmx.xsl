<?xml version="1.0" encoding="UTF-8"?>
<!--
  lift-to-tmx.xsl
  Transforms LIFT 0.13 directly to TMX 1.4b (Translation Memory eXchange).
  ITS 1.0 metadata is embedded as TMX <prop> elements with
  type="x-its-*" following the TMX extensibility convention.

  Direction : LIFT → TMX
  Standard refs:
    LIFT — https://github.com/sillsdev/lift-standard
    TMX  — https://www.gala-global.org/tmx-14b
    ITS  — http://www.w3.org/TR/its/

  LIFT glosses and definitions become bilingual TMX <tu> (translation
  unit) elements.  The vernacular headword is the source; each gloss
  language variant is a separate <tuv> (translation unit variant).
-->
<xsl:stylesheet
  xmlns:xsl  = "http://www.w3.org/1999/XSL/Transform"
  xmlns:its  = "http://www.w3.org/2005/11/its"
  version    = "2.0">

  <xsl:output method="xml" encoding="UTF-8" indent="yes"/>
  <xsl:strip-space elements="*"/>

  <!-- ============================================================
       Parameters
       ============================================================ -->
  <xsl:param name="source-lang"    select="'und'"/>
  <xsl:param name="admin-lang"     select="'en'"/>
  <xsl:param name="creationtool"   select="'lift-to-tmx.xsl'"/>
  <xsl:param name="datatype"       select="'PlainText'"/>
  <!-- ISO 8601 creation date; caller should inject current dateTime -->
  <xsl:param name="creationdate"   select="string(current-dateTime())"/>

  <!-- ============================================================
       Root: LIFT <lift>  →  TMX <tmx>
       ============================================================ -->
  <xsl:template match="/lift">
    <tmx version="1.4">
      <header
        creationtool    = "{$creationtool}"
        creationtoolversion = "1.0"
        datatype        = "{$datatype}"
        segtype         = "sentence"
        adminlang       = "{$admin-lang}"
        srclang         = "{$source-lang}"
        creationdate    = "{$creationdate}">

        <!--
          ITS rules embedded as TMX notes.
          TMX <note> is the conventional carrier for process metadata.
        -->
        <note xml:lang="{$admin-lang}">
          ITS rule: grammatical-info nodes are translate="no"
        </note>
        <note xml:lang="{$admin-lang}">
          ITS rule: semantic-domain nodes are translate="no"
        </note>

        <!-- TMX property: map LIFT version for round-trip fidelity -->
        <prop type="x-lift-version">
          <xsl:value-of select="@version"/>
        </prop>
        <prop type="x-lift-producer">
          <xsl:value-of select="@producer"/>
        </prop>
      </header>

      <body>
        <xsl:apply-templates select="entry"/>
      </body>
    </tmx>
  </xsl:template>

  <!-- ============================================================
       LIFT <entry>  →  one or more TMX <tu> elements
       One <tu> per sense × gloss-language combination.
       ============================================================ -->
  <xsl:template match="entry">
    <xsl:variable name="entry-id"
                  select="if (@id) then @id else generate-id()"/>
    <xsl:variable name="headword"
                  select="(lexical-unit/form[@lang=$source-lang]/text/text()
                           | lexical-unit/form[1]/text/text())[1]"/>
    <xsl:variable name="headword-lang"
                  select="(lexical-unit/form[@lang=$source-lang]/@lang
                           | lexical-unit/form[1]/@lang)[1]"/>

    <xsl:for-each select="sense">
      <xsl:variable name="sense-pos" select="position()"/>
      <xsl:variable name="sense-id"
                    select="if (@id) then @id
                            else concat($entry-id,'.sense.',$sense-pos)"/>
      <xsl:variable name="gram-info"
                    select="grammatical-info/@value"/>

      <!-- A tu per gloss language -->
      <xsl:for-each select="gloss">
        <xsl:variable name="gloss-lang" select="@lang"/>
        <xsl:variable name="gloss-text" select="text/text()"/>

        <tu tuid    = "{$sense-id}.gloss.{$gloss-lang}"
            datatype= "{$datatype}"
            creationdate="{$creationdate}">

          <!-- ITS-derived TMX props on the <tu> -->
          <xsl:if test="$gram-info">
            <prop type="x-its-translate-no">grammatical-info</prop>
            <prop type="x-grammatical-info">
              <xsl:value-of select="$gram-info"/>
            </prop>
          </xsl:if>

          <xsl:for-each select="../semantic-domain">
            <prop type="x-its-translate-no">semantic-domain</prop>
            <prop type="x-semantic-domain">
              <xsl:value-of select="@name"/>
            </prop>
          </xsl:for-each>

          <!-- Relation cross-references -->
          <xsl:for-each select="../../relation">
            <prop type="x-lift-relation-type">
              <xsl:value-of select="@type"/>
            </prop>
            <prop type="x-lift-relation-ref">
              <xsl:value-of select="@ref"/>
            </prop>
          </xsl:for-each>

          <!-- Entry-level metadata (non-translatable) -->
          <prop type="x-lift-entry-id"><xsl:value-of select="$entry-id"/></prop>
          <prop type="x-lift-sense-id"><xsl:value-of select="$sense-id"/></prop>
          <prop type="x-lift-morph-type"><xsl:value-of select="../../@morph-type"/></prop>

          <!-- Source TUV — vernacular headword -->
          <tuv xml:lang="{$headword-lang}">
            <seg><xsl:value-of select="$headword"/></seg>
          </tuv>

          <!-- Target TUV — gloss in analysis language -->
          <tuv xml:lang="{$gloss-lang}">
            <seg><xsl:value-of select="$gloss-text"/></seg>
          </tuv>

        </tu>
      </xsl:for-each>

      <!-- Definition-based TUs (richer than gloss) -->
      <xsl:for-each select="definition/form">
        <xsl:variable name="def-lang" select="@lang"/>
        <tu tuid     = "{$sense-id}.definition.{$def-lang}"
            datatype = "{$datatype}"
            creationdate="{$creationdate}">

          <prop type="x-lift-entry-id"><xsl:value-of select="$entry-id"/></prop>
          <prop type="x-lift-sense-id"><xsl:value-of select="$sense-id"/></prop>
          <prop type="x-tu-restype">definition</prop>

          <xsl:if test="$gram-info">
            <prop type="x-grammatical-info">
              <xsl:value-of select="$gram-info"/>
            </prop>
          </xsl:if>

          <tuv xml:lang="{$headword-lang}">
            <seg><xsl:value-of select="$headword"/></seg>
          </tuv>
          <tuv xml:lang="{$def-lang}">
            <seg><xsl:value-of select="text"/></seg>
          </tuv>
        </tu>
      </xsl:for-each>

      <!-- Example sentence TUs -->
      <xsl:for-each select="example">
        <xsl:variable name="ex-pos" select="position()"/>
        <xsl:for-each select="form[@lang=$source-lang]">
          <xsl:if test="../translation/form">
            <tu tuid     = "{$sense-id}.example.{$ex-pos}"
                datatype = "{$datatype}"
                segtype  = "sentence"
                creationdate="{$creationdate}">
              <prop type="x-lift-entry-id"><xsl:value-of select="$entry-id"/></prop>
              <prop type="x-tu-restype">example</prop>

              <tuv xml:lang="{@lang}">
                <seg><xsl:value-of select="text"/></seg>
              </tuv>
              <xsl:for-each select="../translation/form">
                <tuv xml:lang="{@lang}">
                  <seg><xsl:value-of select="text"/></seg>
                </tuv>
              </xsl:for-each>
            </tu>
          </xsl:if>
        </xsl:for-each>
      </xsl:for-each>

    </xsl:for-each>
  </xsl:template>

  <xsl:template match="text()"/>

</xsl:stylesheet>
