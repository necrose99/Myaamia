<?xml version="1.0" encoding="UTF-8"?>
<!--
  xdxf2xliff.xsl  —  XDXF rev34 → XLIFF 2.0
  Compatible: Saxon-HE 12, xsltproc (XSLT 1.0)

  Each <ar> → one <unit>.
  First <k> → <source>.
  Each language-tagged <def> → separate XLIFF <file> block grouped by trgLang,
  or if only one target lang, a single <file>.
  <co> → <note>
  <gr> → <mda:meta type="x-pos">
  <categ><kref> → <mda:meta type="domain">
  <etm> → <mda:meta type="x-etymology">
  <ex> → <note category="example">
  Glossary module populated if <kref type="syn|ant"> present.
-->
<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns="urn:oasis:names:tc:xliff:document:2.0"
    xmlns:mda="urn:oasis:names:tc:xliff:metadata:2.0"
    xmlns:gls="urn:oasis:names:tc:xliff:glossary:2.0">

  <xsl:output method="xml" encoding="UTF-8" indent="yes"/>
  <xsl:strip-space elements="*"/>

  <!-- ═══════════════════════════════════════════════════════════
       Parameters
  ═══════════════════════════════════════════════════════════════ -->
  <!-- Override to emit only one target lang:  - param trgLang "'fr'" -->
  <xsl:param name="trgLang" select="''"/>

  <!-- ═══════════════════════════════════════════════════════════
       Root
  ═══════════════════════════════════════════════════════════════ -->
  <xsl:template match="/">
    <xsl:apply-templates select="xdxf"/>
  </xsl:template>

  <xsl:template match="xdxf">
    <xsl:variable name="srcLang"
      select="meta_info/languages/from[1]/@xml:lang"/>

    <!-- Resolve target lang: param > first <to> -->
    <xsl:variable name="resolvedTrg">
      <xsl:choose>
        <xsl:when test="$trgLang != ''">
          <xsl:value-of select="$trgLang"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:value-of select="meta_info/languages/to[1]/@xml:lang"/>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:variable>

    <xliff version="2.0">
      <xsl:attribute name="srcLang">
        <xsl:value-of select="$srcLang"/>
      </xsl:attribute>
      <xsl:attribute name="trgLang">
        <xsl:value-of select="$resolvedTrg"/>
      </xsl:attribute>

      <file>
        <xsl:attribute name="id">f1</xsl:attribute>
        <xsl:attribute name="original">
          <xsl:value-of select="meta_info/title"/>
        </xsl:attribute>

        <xsl:apply-templates select="lexicon/ar">
          <xsl:with-param name="srcLang" select="$srcLang"/>
          <xsl:with-param name="trgLang" select="$resolvedTrg"/>
        </xsl:apply-templates>

      </file>
    </xliff>
  </xsl:template>

  <!-- ═══════════════════════════════════════════════════════════
       <ar> → <unit>
  ═══════════════════════════════════════════════════════════════ -->
  <xsl:template match="ar">
    <xsl:param name="srcLang"/>
    <xsl:param name="trgLang"/>

    <!-- Generate deterministic id from position -->
    <xsl:variable name="uid">
      <xsl:text>u</xsl:text>
      <xsl:number count="ar" level="any"/>
    </xsl:variable>

    <unit>
      <xsl:attribute name="id">
        <xsl:value-of select="$uid"/>
      </xsl:attribute>
      <!-- Use headword as name (translation key) -->
      <xsl:attribute name="name">
        <xsl:value-of select="translate(normalize-space(k[1]),
          ' /\:;,()[]{}',
          '____________')"/>
      </xsl:attribute>

      <!-- ── Metadata module ── -->
      <xsl:if test=".//gr or .//categ or .//etm">
        <mda:metadata>
          <mda:metaGroup>
            <xsl:if test=".//gr">
              <mda:meta type="x-pos">
                <xsl:value-of select="(.//gr)[1]"/>
              </mda:meta>
            </xsl:if>
            <xsl:for-each select=".//categ/kref">
              <mda:meta type="domain">
                <xsl:value-of select="."/>
              </mda:meta>
            </xsl:for-each>
            <xsl:if test=".//etm">
              <mda:meta type="x-etymology">
                <xsl:value-of select="(.//etm)[1]"/>
              </mda:meta>
            </xsl:if>
          </mda:metaGroup>
        </mda:metadata>
      </xsl:if>

      <!-- ── Glossary module: synonyms/antonyms ── -->
      <xsl:if test=".//sr/kref[@type='syn' or @type='ant']">
        <gls:glossary>
          <xsl:for-each select=".//sr/kref[@type='syn']">
            <gls:glossEntry>
              <gls:term><xsl:value-of select="."/></gls:term>
              <gls:definition>synonym</gls:definition>
            </gls:glossEntry>
          </xsl:for-each>
          <xsl:for-each select=".//sr/kref[@type='ant']">
            <gls:glossEntry>
              <gls:term><xsl:value-of select="."/></gls:term>
              <gls:definition>antonym</gls:definition>
            </gls:glossEntry>
          </xsl:for-each>
        </gls:glossary>
      </xsl:if>

      <!-- ── Notes: co + examples ── -->
      <xsl:if test=".//co or .//ex">
        <notes>
          <xsl:for-each select=".//co">
            <note>
              <xsl:if test="@type != ''">
                <xsl:attribute name="category">
                  <xsl:value-of select="@type"/>
                </xsl:attribute>
              </xsl:if>
              <xsl:value-of select="."/>
            </note>
          </xsl:for-each>
          <xsl:for-each select=".//ex">
            <note category="example">
              <xsl:value-of select="ex_orig[1]"/>
              <xsl:if test="ex_tran">
                <xsl:text> → </xsl:text>
                <xsl:value-of select="ex_tran[1]"/>
              </xsl:if>
            </note>
          </xsl:for-each>
        </notes>
      </xsl:if>

      <!-- ── Segment: source + target ── -->
      <xsl:variable name="segId">
        <xsl:value-of select="$uid"/>
        <xsl:text>s1</xsl:text>
      </xsl:variable>

      <segment>
        <xsl:attribute name="id"><xsl:value-of select="$segId"/></xsl:attribute>

        <source><xsl:value-of select="k[1]"/></source>

        <!-- Find matching target def by xml:lang -->
        <xsl:variable name="tgt">
          <xsl:call-template name="find-def-text">
            <xsl:with-param name="def" select="def"/>
            <xsl:with-param name="lang" select="$trgLang"/>
            <xsl:with-param name="inheritLang" select="''"/>
          </xsl:call-template>
        </xsl:variable>

        <xsl:choose>
          <xsl:when test="normalize-space($tgt) != ''">
            <target state="translated">
              <xsl:value-of select="$tgt"/>
            </target>
          </xsl:when>
          <xsl:otherwise>
            <target state="initial"/>
          </xsl:otherwise>
        </xsl:choose>
      </segment>

    </unit>
  </xsl:template>

  <!-- ═══════════════════════════════════════════════════════════
       Helper: find deftext for a given target language
       Walks def recursively, inheriting xml:lang downward.
  ═══════════════════════════════════════════════════════════════ -->
  <xsl:template name="find-def-text">
    <xsl:param name="def"/>
    <xsl:param name="lang"/>
    <xsl:param name="inheritLang"/>

    <xsl:for-each select="$def">
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
        <!-- Leaf def matching requested lang -->
        <xsl:when test="deftext and not(def) and
            (translate($myLang,'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
                              'abcdefghijklmnopqrstuvwxyz')
             = translate($lang,'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
                               'abcdefghijklmnopqrstuvwxyz')
             or $lang = '')">
          <xsl:value-of select="deftext"/>
        </xsl:when>
        <!-- Recurse into child defs -->
        <xsl:otherwise>
          <xsl:call-template name="find-def-text">
            <xsl:with-param name="def" select="def"/>
            <xsl:with-param name="lang" select="$lang"/>
            <xsl:with-param name="inheritLang" select="$myLang"/>
          </xsl:call-template>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:for-each>
  </xsl:template>

</xsl:stylesheet>
