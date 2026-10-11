<?xml version="1.0" encoding="UTF-8"?>
<!--
  xdxf2tmx.xsl  —  XDXF rev34 → TMX 1.4b
  Compatible: Saxon-HE 12, xsltproc (XSLT 1.0)

  Every <ar> yields one <tu>.
  The source <k> becomes the source <tuv>.
  Each language-tagged <def xml:lang="xx"> yields a target <tuv xml:lang="xx">.
  Nested <def> blocks are flattened; xml:lang is inherited downward.
  <co> → <note>
  <categ><kref> → <prop type="domain">
  <ex><ex_orig>/<ex_tran> → <prop type="x-example">
  <gr> → <prop type="x-pos">
  <etm> → <prop type="x-etymology">
-->
<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output method="xml" encoding="UTF-8" indent="yes"/>
  <xsl:strip-space elements="*"/>

  <!-- ═══════════════════════════════════════════════════════════
       Root
  ═══════════════════════════════════════════════════════════════ -->
  <xsl:template match="/">
    <xsl:apply-templates select="xdxf"/>
  </xsl:template>

  <xsl:template match="xdxf">
    <xsl:variable name="srcLang"
      select="meta_info/languages/from/@xml:lang"/>

    <tmx version="1.4">
      <header
        creationtool="xdxf2tmx.xsl"
        creationtoolversion="1.0"
        datatype="plaintext"
        segtype="phrase"
        adminlang="en"
        srclang="{$srcLang}"
        o-tmf="XDXF"/>
      <body>
        <xsl:apply-templates select="lexicon/ar">
          <xsl:with-param name="srcLang" select="$srcLang"/>
        </xsl:apply-templates>
      </body>
    </tmx>
  </xsl:template>

  <!-- ═══════════════════════════════════════════════════════════
       <ar> → <tu>
  ═══════════════════════════════════════════════════════════════ -->
  <xsl:template match="ar">
    <xsl:param name="srcLang"/>

    <tu>
      <xsl:if test="k/@id != ''">
        <xsl:attribute name="tuid">
          <xsl:value-of select="k[1]/@id"/>
        </xsl:attribute>
      </xsl:if>

      <!-- Part-of-speech prop -->
      <xsl:if test=".//gr">
        <prop type="x-pos">
          <xsl:value-of select="(.//gr)[1]"/>
        </prop>
      </xsl:if>

      <!-- Commentary as note -->
      <xsl:for-each select=".//co">
        <note>
          <xsl:value-of select="."/>
        </note>
      </xsl:for-each>

      <!-- Category as domain prop -->
      <xsl:for-each select=".//categ/kref">
        <prop type="domain">
          <xsl:value-of select="."/>
        </prop>
      </xsl:for-each>

      <!-- Examples as props -->
      <xsl:for-each select=".//ex">
        <prop type="x-example">
          <xsl:value-of select="ex_orig[1]"/>
          <xsl:if test="ex_tran">
            <xsl:text> | </xsl:text>
            <xsl:value-of select="ex_tran[1]"/>
          </xsl:if>
        </prop>
      </xsl:for-each>

      <!-- Etymology as prop -->
      <xsl:if test=".//etm">
        <prop type="x-etymology">
          <xsl:value-of select="(.//etm)[1]"/>
        </prop>
      </xsl:if>

      <!-- Source tuv from first <k> -->
      <tuv>
        <xsl:attribute name="xml:lang">
          <xsl:choose>
            <xsl:when test="k[1]/@xml:lang != ''">
              <xsl:value-of select="k[1]/@xml:lang"/>
            </xsl:when>
            <xsl:otherwise>
              <xsl:value-of select="$srcLang"/>
            </xsl:otherwise>
          </xsl:choose>
        </xsl:attribute>
        <seg><xsl:value-of select="k[1]"/></seg>
      </tuv>

      <!-- Alternate headwords as extra source tuvs with same lang -->
      <xsl:for-each select="k[position() > 1]">
        <tuv>
          <xsl:attribute name="xml:lang">
            <xsl:choose>
              <xsl:when test="@xml:lang != ''">
                <xsl:value-of select="@xml:lang"/>
              </xsl:when>
              <xsl:otherwise>
                <xsl:value-of select="$srcLang"/>
              </xsl:otherwise>
            </xsl:choose>
          </xsl:attribute>
          <seg><xsl:value-of select="."/></seg>
        </tuv>
      </xsl:for-each>

      <!-- Target tuvs: one per language-tagged def.
           Walk def tree, collect (lang, text) pairs, emit tuv for each. -->
      <xsl:apply-templates select="def" mode="tuv">
        <xsl:with-param name="inheritLang" select="''"/>
      </xsl:apply-templates>

    </tu>
  </xsl:template>

  <!-- Recursive def walker: emit a <tuv> for each leaf deftext with a lang -->
  <xsl:template match="def" mode="tuv">
    <xsl:param name="inheritLang"/>
    <xsl:variable name="myLang">
      <xsl:choose>
        <xsl:when test="@xml:lang != ''">
          <xsl:value-of select="@xml:lang"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:value-of select="$inheritLang"/>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:variable>

    <xsl:choose>
      <!-- Leaf def: has deftext, no child def elements -->
      <xsl:when test="deftext and not(def)">
        <xsl:if test="$myLang != ''">
          <tuv>
            <xsl:attribute name="xml:lang">
              <xsl:value-of select="$myLang"/>
            </xsl:attribute>
            <seg><xsl:value-of select="deftext"/></seg>
          </tuv>
        </xsl:if>
      </xsl:when>
      <!-- Composite def: recurse -->
      <xsl:otherwise>
        <xsl:apply-templates select="def" mode="tuv">
          <xsl:with-param name="inheritLang" select="$myLang"/>
        </xsl:apply-templates>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

</xsl:stylesheet>
