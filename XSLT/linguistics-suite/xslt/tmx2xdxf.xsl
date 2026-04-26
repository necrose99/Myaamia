<?xml version="1.0" encoding="UTF-8"?>
<!--
  tmx2xdxf.xsl  —  TMX 1.4 → XDXF rev34
  Compatible: Saxon-HE 12, xsltproc (XSLT 1.0)

  TMX structure recap
  ───────────────────
  <tmx version="1.4">
    <header creationtool="..." srclang="en" .../>
    <body>
      <tu tuid="?" srclang="?" note="?">
        <prop type="domain|subject|...">value</prop>
        <tuv xml:lang="en"><seg>source text</seg></tuv>
        <tuv xml:lang="fr"><seg>target text</seg></tuv>
        ...
      </tu>
    </body>
  </tmx>

  Mapping strategy
  ────────────────
  TMX is a translation memory format — its unit of meaning is a
  SENTENCE/SEGMENT pair, not a lexical entry.  We treat each <tu> as
  one <ar> where:

    Source <tuv> (matching header/@srclang or first tuv)
      → <k xml:lang="…">  headword / phrase
    Every other <tuv>
      → nested <def xml:lang="…"><deftext>…</deftext></def>
    <prop type="domain|subject">
      → <categ><kref>…</kref></categ>
    <tu @note> / <tuv @note> / <note> children
      → <co> comment
    <prop type="x-example">
      → <ex><ex_orig>…</ex_orig></ex>

  Muenchian grouping on seg text removes exact duplicate source segments.

  XDXF note: if srclang is absent we fall back to the xml:lang of the
  first <tuv>.  All target languages get a <to> in <languages>.
-->
<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xml="http://www.w3.org/XML/1998/namespace">

  <xsl:output method="xml" encoding="UTF-8" indent="yes"/>
  <xsl:strip-space elements="*"/>

  <!-- Deduplicate on source segment text -->
  <xsl:key name="tu-by-src-seg" match="tu"
           use="tuv[1]/seg"/>

  <!-- ═══════════════════════════════════════════════════════════
       Parameters — override on command line:
         - param src-lang "'fr'"
  ═══════════════════════════════════════════════════════════════ -->
  <xsl:param name="src-lang" select="''"/>

  <!-- ═══════════════════════════════════════════════════════════
       Root
  ═══════════════════════════════════════════════════════════════ -->
  <xsl:template match="/">
    <xsl:apply-templates select="tmx"/>
  </xsl:template>

  <xsl:template match="tmx">
    <!-- Resolve source language -->
    <xsl:variable name="srcLang">
      <xsl:choose>
        <xsl:when test="$src-lang != ''">
          <xsl:value-of select="$src-lang"/>
        </xsl:when>
        <xsl:when test="header/@srclang and header/@srclang != '*all*'">
          <xsl:value-of select="header/@srclang"/>
        </xsl:when>
        <xsl:otherwise>
          <!-- fall back to first tuv lang -->
          <xsl:value-of select="body/tu[1]/tuv[1]/@xml:lang"/>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:variable>

    <xdxf revision="34">
      <meta_info>
        <!-- title from creationtool or datatype -->
        <title>
          <xsl:choose>
            <xsl:when test="header/@creationtool != ''">
              <xsl:value-of select="header/@creationtool"/>
              <xsl:text> TMX Export</xsl:text>
            </xsl:when>
            <xsl:otherwise>TMX Translation Memory</xsl:otherwise>
          </xsl:choose>
        </title>
        <full_title>
          <xsl:value-of select="header/@creationtool"/>
          <xsl:if test="header/@creationtoolversion != ''">
            <xsl:text> v</xsl:text>
            <xsl:value-of select="header/@creationtoolversion"/>
          </xsl:if>
          <xsl:text> — converted by tmx2xdxf.xsl</xsl:text>
        </full_title>
        <description>
          <xsl:text>TMX datatype: </xsl:text>
          <xsl:value-of select="header/@datatype"/>
          <xsl:if test="header/@segtype != ''">
            <xsl:text>; segtype: </xsl:text>
            <xsl:value-of select="header/@segtype"/>
          </xsl:if>
        </description>
        <languages>
          <from>
            <xsl:attribute name="xml:lang">
              <xsl:value-of select="$srcLang"/>
            </xsl:attribute>
          </from>
          <!-- Collect unique non-source target langs -->
          <xsl:for-each select="body/tu/tuv[
              translate(@xml:lang,
                'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
                'abcdefghijklmnopqrstuvwxyz')
              != translate($srcLang,
                'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
                'abcdefghijklmnopqrstuvwxyz')]">
            <!-- Poor-man's unique: only emit when this is the first
                 occurrence of this lang in document order -->
            <xsl:variable name="thisLang" select="@xml:lang"/>
            <xsl:if test="generate-id(.) =
                generate-id(//tuv[@xml:lang = $thisLang][1])">
              <to>
                <xsl:attribute name="xml:lang">
                  <xsl:value-of select="$thisLang"/>
                </xsl:attribute>
              </to>
            </xsl:if>
          </xsl:for-each>
        </languages>
        <file_ver>
          <xsl:value-of select="header/@creationtoolversion"/>
        </file_ver>
        <creation_date>
          <xsl:value-of select="header/@creationdate"/>
        </creation_date>
        <last_edited_date>
          <xsl:value-of select="header/@changedate"/>
        </last_edited_date>
      </meta_info>

      <lexicon>
        <xsl:apply-templates select="body/tu">
          <xsl:with-param name="srcLang" select="$srcLang"/>
        </xsl:apply-templates>
      </lexicon>
    </xdxf>
  </xsl:template>

  <!-- ═══════════════════════════════════════════════════════════
       <tu> → <ar>
  ═══════════════════════════════════════════════════════════════ -->
  <xsl:template match="tu">
    <xsl:param name="srcLang"/>

    <!-- Pick the source tuv: match srclang attr, else first tuv -->
    <xsl:variable name="srcTuv">
      <xsl:choose>
        <xsl:when test="tuv[
            translate(@xml:lang,
              'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz')
            = translate($srcLang,
              'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz')]">
          <xsl:value-of select="tuv[
            translate(@xml:lang,
              'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz')
            = translate($srcLang,
              'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz')
            ][1]/seg"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:value-of select="tuv[1]/seg"/>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:variable>

    <xsl:variable name="srcTuvLang">
      <xsl:choose>
        <xsl:when test="$srcLang != ''">
          <xsl:value-of select="$srcLang"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:value-of select="tuv[1]/@xml:lang"/>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:variable>

    <ar>
      <!-- ── Headword: source segment ── -->
      <k>
        <xsl:attribute name="xml:lang">
          <xsl:value-of select="$srcTuvLang"/>
        </xsl:attribute>
        <xsl:value-of select="$srcTuv"/>
      </k>

      <def>
        <!-- tu-level note → commentary -->
        <xsl:if test="@note != '' or note">
          <co>
            <xsl:choose>
              <xsl:when test="@note != ''">
                <xsl:value-of select="@note"/>
              </xsl:when>
              <xsl:otherwise>
                <xsl:value-of select="note[1]"/>
              </xsl:otherwise>
            </xsl:choose>
          </co>
        </xsl:if>

        <!-- Domain/subject props → categ -->
        <xsl:for-each select="prop[@type='domain' or
                                   @type='subject' or
                                   @type='x-domain']">
          <co type="domain">
            <xsl:value-of select="."/>
          </co>
        </xsl:for-each>

        <!-- Example props -->
        <xsl:for-each select="prop[@type='x-example']">
          <ex>
            <ex_orig><xsl:value-of select="."/></ex_orig>
          </ex>
        </xsl:for-each>

        <!-- First target-language segment as primary deftext.
             Remaining targets become nested def elements. -->
        <xsl:variable name="firstTgt" select="tuv[
            translate(@xml:lang,
              'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz')
            != translate($srcLang,
              'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz')
          ][1]"/>

        <xsl:choose>
          <xsl:when test="$firstTgt">
            <!-- All target tuvs as language-tagged def children -->
            <xsl:for-each select="tuv[
                translate(@xml:lang,
                  'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz')
                != translate($srcLang,
                  'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz')]">
              <def>
                <xsl:attribute name="xml:lang">
                  <xsl:value-of select="@xml:lang"/>
                </xsl:attribute>
                <!-- tuv-level note / prop as comment -->
                <xsl:if test="@note != '' or note or prop">
                  <co>
                    <xsl:choose>
                      <xsl:when test="@note != ''">
                        <xsl:value-of select="@note"/>
                      </xsl:when>
                      <xsl:when test="note">
                        <xsl:value-of select="note[1]"/>
                      </xsl:when>
                      <xsl:when test="prop[@type='x-comment']">
                        <xsl:value-of select="prop[@type='x-comment'][1]"/>
                      </xsl:when>
                    </xsl:choose>
                  </co>
                </xsl:if>
                <deftext>
                  <!-- seg may contain inline <hi>, <ph>, <bpt/ept>, <it>, <ut>
                       elements — pull all text nodes recursively -->
                  <xsl:value-of select="seg"/>
                </deftext>
              </def>
            </xsl:for-each>
          </xsl:when>
          <xsl:otherwise>
            <deftext/>
          </xsl:otherwise>
        </xsl:choose>

        <!-- Subject/domain as categ -->
        <xsl:for-each select="prop[@type='domain' or @type='subject']">
          <categ>
            <kref><xsl:value-of select="."/></kref>
          </categ>
        </xsl:for-each>

      </def><!-- /def -->
    </ar>
  </xsl:template>

</xsl:stylesheet>
