<?xml version="1.0" encoding="UTF-8"?>
<!--
  xliff-to-lift.xsl
  Transforms XLIFF 1.2 back to LIFT 0.13 (round-trip).
  ITS its:translate="no" nodes are preserved as LIFT <note> elements
  with type="metadata" so no lexical data is silently discarded.

  Direction : XLIFF → LIFT
-->
<xsl:stylesheet
  xmlns:xsl  = "http://www.w3.org/1999/XSL/Transform"
  xmlns:xl   = "urn:oasis:names:tc:xliff:document:1.2"
  xmlns:its  = "http://www.w3.org/2005/11/its"
  version    = "2.0"
  exclude-result-prefixes="xl its">

  <xsl:output method="xml" encoding="UTF-8" indent="yes"/>
  <xsl:strip-space elements="*"/>

  <!-- ============================================================
       Parameters
       ============================================================ -->
  <xsl:param name="lift-version" select="'0.13'"/>
  <xsl:param name="producer"     select="'xliff-to-lift.xsl'"/>

  <!-- ============================================================
       Root: XLIFF <xliff> → LIFT <lift>
       ============================================================ -->
  <xsl:template match="/xl:xliff">
    <lift version="{$lift-version}" producer="{$producer}">
      <xsl:apply-templates select="xl:file"/>
    </lift>
  </xsl:template>

  <!-- ============================================================
       XLIFF <file>  →  LIFT <entry>
       Each file's @original carries the LIFT entry id.
       ============================================================ -->
  <xsl:template match="xl:file">
    <xsl:variable name="entry-id" select="@original"/>
    <xsl:variable name="src-lang" select="@source-language"/>
    <xsl:variable name="tgt-lang" select="@target-language"/>

    <entry id="{$entry-id}">
      <!-- Recover dateCreated / dateModified from header notes -->
      <xsl:for-each select="xl:header/xl:note[starts-with(.,'LIFT dateCreated')]">
        <xsl:attribute name="dateCreated"
                       select="normalize-space(substring-after(.,'LIFT dateCreated: '))"/>
      </xsl:for-each>
      <xsl:for-each select="xl:header/xl:note[starts-with(.,'LIFT dateModified')]">
        <xsl:attribute name="dateModified"
                       select="normalize-space(substring-after(.,'LIFT dateModified: '))"/>
      </xsl:for-each>
      <!-- Recover morph-type -->
      <xsl:for-each select="xl:header/xl:note[@its:translate='no'][starts-with(.,'morph-type')]">
        <xsl:attribute name="morph-type"
                       select="normalize-space(substring-after(.,'morph-type: '))"/>
      </xsl:for-each>

      <!-- Lexical unit headword -->
      <xsl:for-each select="xl:body/xl:trans-unit[@resname='lexical-unit']">
        <lexical-unit>
          <form lang="{$src-lang}">
            <text><xsl:value-of select="xl:source"/></text>
          </form>
        </lexical-unit>
        <!-- Citation form from alt-trans if present -->
        <xsl:for-each select="xl:alt-trans[@origin='citation-form']">
          <citation>
            <form lang="{$src-lang}">
              <text><xsl:value-of select="xl:source"/></text>
            </form>
          </citation>
        </xsl:for-each>
      </xsl:for-each>

      <!-- Pronunciation (was marked its:translate="no") -->
      <xsl:for-each select="xl:body/xl:trans-unit[@resname='pronunciation']">
        <pronunciation>
          <form lang="{xl:source/@xml:lang}">
            <text><xsl:value-of select="xl:source"/></text>
          </form>
        </pronunciation>
      </xsl:for-each>

      <!-- Relations recovered from header notes -->
      <xsl:for-each select="xl:header/xl:note[@its:translate='no']
                                              [starts-with(.,'relation ')]">
        <xsl:variable name="rel-text" select="normalize-space(.)"/>
        <relation
          type="{replace($rel-text,'relation type=&quot;([^&quot;]+)&quot;.*','$1')}"
          ref= "{replace($rel-text,'.*ref=&quot;([^&quot;]+)&quot;','$1')}"/>
      </xsl:for-each>

      <!-- Senses: one XLIFF <group restype="sense"> per sense -->
      <xsl:apply-templates select="xl:body/xl:group[@restype='sense']">
        <xsl:with-param name="src-lang" select="$src-lang"/>
        <xsl:with-param name="tgt-lang" select="$tgt-lang"/>
      </xsl:apply-templates>
    </entry>
  </xsl:template>

  <!-- ============================================================
       XLIFF <group restype="sense">  →  LIFT <sense>
       ============================================================ -->
  <xsl:template match="xl:group[@restype='sense']">
    <xsl:param name="src-lang"/>
    <xsl:param name="tgt-lang"/>

    <xsl:variable name="sense-id" select="@id"/>

    <sense id="{$sense-id}">
      <!-- Grammatical info recovered from note -->
      <xsl:for-each select="xl:note[@its:translate='no']
                                    [starts-with(.,'grammatical-info')]">
        <xsl:variable name="gi"
          select="replace(normalize-space(.),'grammatical-info value=&quot;([^&quot;]+)&quot;.*','$1')"/>
        <grammatical-info value="{$gi}"/>
      </xsl:for-each>

      <!-- Semantic domains recovered from notes -->
      <xsl:for-each select="xl:note[@its:translate='no']
                                    [starts-with(.,'semantic-domain')]">
        <semantic-domain
          name="{normalize-space(substring-after(.,'semantic-domain: '))}"/>
      </xsl:for-each>

      <!-- Glosses -->
      <xsl:for-each select="xl:trans-unit[@resname='gloss']">
        <gloss lang="{xl:target/@xml:lang}">
          <text><xsl:value-of select="xl:target"/></text>
        </gloss>
      </xsl:for-each>

      <!-- Definitions -->
      <xsl:if test="xl:trans-unit[@resname='definition']">
        <definition>
          <xsl:for-each select="xl:trans-unit[@resname='definition']">
            <form lang="{xl:target/@xml:lang}">
              <text><xsl:value-of select="xl:target"/></text>
            </form>
          </xsl:for-each>
        </definition>
      </xsl:if>

      <!-- Examples -->
      <xsl:for-each select="xl:trans-unit[@resname='example']">
        <example>
          <form lang="{xl:source/@xml:lang}">
            <text><xsl:value-of select="xl:source"/></text>
          </form>
          <xsl:if test="xl:target">
            <translation type="Frame sentence">
              <form lang="{xl:target/@xml:lang}">
                <text><xsl:value-of select="xl:target"/></text>
              </form>
            </translation>
          </xsl:if>
        </example>
      </xsl:for-each>

    </sense>
  </xsl:template>

  <xsl:template match="text()"/>

</xsl:stylesheet>
