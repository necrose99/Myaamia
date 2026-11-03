<?xml version="1.0" encoding="UTF-8"?>
<!--
  tmx-to-lift.xsl
  Reconstructs LIFT 0.13 from TMX 1.4b produced by lift-to-tmx.xsl.
  Uses x-lift-* <prop> values to rebuild the LIFT entry/sense hierarchy.

  Direction : TMX → LIFT
  Note: TMX is inherently flat (a list of TUs); reconstruction groups
  TUs by x-lift-entry-id then x-lift-sense-id using XSLT 2.0
  grouping (<xsl:for-each-group>).
-->
<xsl:stylesheet
  xmlns:xsl = "http://www.w3.org/1999/XSL/Transform"
  version   = "2.0">

  <xsl:output method="xml" encoding="UTF-8" indent="yes"/>
  <xsl:strip-space elements="*"/>

  <!-- ============================================================
       Parameters
       ============================================================ -->
  <xsl:param name="lift-version"
             select="(/tmx/header/prop[@type='x-lift-version'],'0.13')[1]"/>
  <xsl:param name="producer"
             select="(/tmx/header/prop[@type='x-lift-producer'],'tmx-to-lift.xsl')[1]"/>
  <xsl:param name="source-lang"
             select="/tmx/header/@srclang"/>

  <!-- ============================================================
       Root: TMX <tmx>  →  LIFT <lift>
       ============================================================ -->
  <xsl:template match="/tmx">
    <lift version="{$lift-version}" producer="{$producer}">
      <xsl:apply-templates select="body"/>
    </lift>
  </xsl:template>

  <!-- ============================================================
       <body>: group TUs by entry-id
       ============================================================ -->
  <xsl:template match="body">
    <xsl:for-each-group select="tu" group-by="prop[@type='x-lift-entry-id']">
      <xsl:call-template name="make-entry">
        <xsl:with-param name="entry-id"
                        select="current-grouping-key()"/>
        <xsl:with-param name="tus"
                        select="current-group()"/>
      </xsl:call-template>
    </xsl:for-each-group>
  </xsl:template>

  <!-- ============================================================
       Named template: build one LIFT <entry> from a group of TUs
       ============================================================ -->
  <xsl:template name="make-entry">
    <xsl:param name="entry-id"/>
    <xsl:param name="tus"/>

    <!-- Use the first headword TU for lexical-unit -->
    <xsl:variable name="first-tu" select="$tus[1]"/>
    <xsl:variable name="src-tuv"
                  select="$first-tu/tuv[@xml:lang=$source-lang]"/>
    <xsl:variable name="morph-type"
                  select="$first-tu/prop[@type='x-lift-morph-type']"/>

    <entry id="{$entry-id}">
      <xsl:if test="normalize-space($morph-type) != ''">
        <xsl:attribute name="morph-type"
                       select="normalize-space($morph-type)"/>
      </xsl:if>

      <lexical-unit>
        <form lang="{$source-lang}">
          <text><xsl:value-of select="$src-tuv/seg"/></text>
        </form>
      </lexical-unit>

      <!-- Reconstruct relations from prop values (deduplicated) -->
      <xsl:for-each-group
        select="$tus/prop[@type='x-lift-relation-ref']"
        group-by=".">
        <xsl:variable name="ref-val" select="current-grouping-key()"/>
        <xsl:variable name="type-val"
          select="(../prop[@type='x-lift-relation-type'])[1]"/>
        <relation type="{$type-val}" ref="{$ref-val}"/>
      </xsl:for-each-group>

      <!-- Group TUs within this entry by sense-id -->
      <xsl:for-each-group select="$tus"
                          group-by="prop[@type='x-lift-sense-id']">
        <xsl:call-template name="make-sense">
          <xsl:with-param name="sense-id"
                          select="current-grouping-key()"/>
          <xsl:with-param name="sense-tus"
                          select="current-group()"/>
        </xsl:call-template>
      </xsl:for-each-group>
    </entry>
  </xsl:template>

  <!-- ============================================================
       Named template: build one LIFT <sense> from sense TU group
       ============================================================ -->
  <xsl:template name="make-sense">
    <xsl:param name="sense-id"/>
    <xsl:param name="sense-tus"/>

    <!-- Grammatical info from first TU that has it -->
    <xsl:variable name="gram-info"
      select="($sense-tus/prop[@type='x-grammatical-info'])[1]"/>

    <sense id="{$sense-id}">
      <xsl:if test="normalize-space($gram-info) != ''">
        <grammatical-info value="{normalize-space($gram-info)}"/>
      </xsl:if>

      <!-- Semantic domains (deduplicated) -->
      <xsl:for-each-group
        select="$sense-tus/prop[@type='x-semantic-domain']"
        group-by=".">
        <semantic-domain name="{current-grouping-key()}"/>
      </xsl:for-each-group>

      <!-- Glosses: TUs with no x-tu-restype are gloss TUs -->
      <xsl:for-each select="$sense-tus[not(prop[@type='x-tu-restype'])]">
        <xsl:for-each select="tuv[not(@xml:lang=$source-lang)]">
          <gloss lang="{@xml:lang}">
            <text><xsl:value-of select="seg"/></text>
          </gloss>
        </xsl:for-each>
      </xsl:for-each>

      <!-- Definitions -->
      <xsl:variable name="def-tus"
        select="$sense-tus[prop[@type='x-tu-restype']='definition']"/>
      <xsl:if test="$def-tus">
        <definition>
          <xsl:for-each select="$def-tus/tuv[not(@xml:lang=$source-lang)]">
            <form lang="{@xml:lang}">
              <text><xsl:value-of select="seg"/></text>
            </form>
          </xsl:for-each>
        </definition>
      </xsl:if>

      <!-- Examples -->
      <xsl:for-each select="$sense-tus[prop[@type='x-tu-restype']='example']">
        <example>
          <form lang="{$source-lang}">
            <text>
              <xsl:value-of select="tuv[@xml:lang=$source-lang]/seg"/>
            </text>
          </form>
          <xsl:for-each select="tuv[not(@xml:lang=$source-lang)]">
            <translation type="Frame sentence">
              <form lang="{@xml:lang}">
                <text><xsl:value-of select="seg"/></text>
              </form>
            </translation>
          </xsl:for-each>
        </example>
      </xsl:for-each>

    </sense>
  </xsl:template>

  <xsl:template match="text()"/>

</xsl:stylesheet>
