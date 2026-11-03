<?xml version="1.0" encoding="UTF-8"?>
<!--
  xliff2xdxf.xsl  - XLIFF 2.x (core + modules) to XDXF rev34
  Compatible: Saxon-HE 12, xsltproc (XSLT 1.0)

  Covers XLIFF 2.0/2.1/2.2 (same core namespace).
  The Symfony xliff-core-2.2.xsd is also handled - it uses the same
  namespace urn:oasis:names:tc:xliff:document:2.0

  Mapping
  unit        - ar
  source      - k xml:lang=srcLang
  target      - def xml:lang=trgLang / deftext
  note        - co
  gls:term    - additional k (glossary module)
  gls:translation - nested def (glossary module)
  mda:meta domain - categ/kref
  unit/@name  - co type=id (translation key name)

  XLIFF 1.2 uses namespace urn:oasis:names:tc:xliff:document:1.2
  and has trans-unit instead of unit/segment. A separate
  sheet (xliff12xdxf.xsl) handles that; both are provided.
-->
<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xl="urn:oasis:names:tc:xliff:document:2.0"
    xmlns:gls="urn:oasis:names:tc:xliff:glossary:2.0"
    xmlns:mda="urn:oasis:names:tc:xliff:metadata:2.0"
    xmlns:mtc="urn:oasis:names:tc:xliff:matches:2.0"
    exclude-result-prefixes="xl gls mda mtc">

  <xsl:output method="xml" encoding="UTF-8" indent="yes"/>
  <xsl:strip-space elements="*"/>

  <!-- ═══════════════════════════════════════════════════════════
       Root
  ═══════════════════════════════════════════════════════════════ -->
  <xsl:template match="/">
    <xsl:apply-templates select="xl:xliff"/>
  </xsl:template>

  <xsl:template match="xl:xliff">
    <xsl:variable name="srcLang" select="@srcLang"/>
    <xsl:variable name="trgLang" select="@trgLang"/>

    <xdxf revision="34">
      <meta_info>
        <title>
          <xsl:choose>
            <xsl:when test="xl:file/@original != ''">
              <xsl:value-of select="xl:file[1]/@original"/>
            </xsl:when>
            <xsl:otherwise>XLIFF Export</xsl:otherwise>
          </xsl:choose>
        </title>
        <full_title>XLIFF <xsl:value-of select="@version"/> — converted by xliff2xdxf.xsl</full_title>
        <description>
          <xsl:text>srcLang: </xsl:text><xsl:value-of select="$srcLang"/>
          <xsl:text>; trgLang: </xsl:text><xsl:value-of select="$trgLang"/>
        </description>
        <languages>
          <from>
            <xsl:attribute name="xml:lang">
              <xsl:choose>
                <xsl:when test="$srcLang != ''">
                  <xsl:value-of select="$srcLang"/>
                </xsl:when>
                <xsl:otherwise>und</xsl:otherwise>
              </xsl:choose>
            </xsl:attribute>
          </from>
          <xsl:choose>
            <xsl:when test="$trgLang != ''">
              <to>
                <xsl:attribute name="xml:lang">
                  <xsl:value-of select="$trgLang"/>
                </xsl:attribute>
              </to>
            </xsl:when>
            <xsl:otherwise>
              <to xml:lang="und"/>
            </xsl:otherwise>
          </xsl:choose>
        </languages>
        <file_ver><xsl:value-of select="@version"/></file_ver>
        <creation_date/>
        <last_edited_date/>
      </meta_info>

      <lexicon>
        <!-- Process all units, including those nested inside groups -->
        <xsl:apply-templates select=".//xl:unit">
          <xsl:with-param name="srcLang" select="$srcLang"/>
          <xsl:with-param name="trgLang" select="$trgLang"/>
        </xsl:apply-templates>
      </lexicon>
    </xdxf>
  </xsl:template>

  <!-- ═══════════════════════════════════════════════════════════
       <unit> → <ar>
       A unit may have multiple <segment> children (e.g. paragraph split).
       We emit one <ar> per unit, merging all segments.
  ═══════════════════════════════════════════════════════════════ -->
  <xsl:template match="xl:unit">
    <xsl:param name="srcLang"/>
    <xsl:param name="trgLang"/>

    <!-- Concatenate all source segments in this unit -->
    <xsl:variable name="srcText">
      <xsl:for-each select="xl:segment/xl:source">
        <xsl:value-of select="normalize-space(.)"/>
        <xsl:if test="position() != last()">
          <xsl:text> </xsl:text>
        </xsl:if>
      </xsl:for-each>
    </xsl:variable>

    <xsl:variable name="trgText">
      <xsl:for-each select="xl:segment/xl:target">
        <xsl:value-of select="normalize-space(.)"/>
        <xsl:if test="position() != last()">
          <xsl:text> </xsl:text>
        </xsl:if>
      </xsl:for-each>
    </xsl:variable>

    <!-- Skip units with no source content -->
    <xsl:if test="normalize-space($srcText) != ''">
      <ar>
        <!-- Glossary module: if present, glossary term is the primary headword -->
        <xsl:choose>
          <xsl:when test="gls:glossary/gls:glossEntry/gls:term">
            <k>
              <xsl:if test="$srcLang != ''">
                <xsl:attribute name="xml:lang">
                  <xsl:value-of select="$srcLang"/>
                </xsl:attribute>
              </xsl:if>
              <xsl:value-of select="gls:glossary/gls:glossEntry/gls:term[1]"/>
            </k>
            <!-- segment source as alternate headword if different -->
            <xsl:if test="normalize-space($srcText) !=
                          normalize-space(gls:glossary/gls:glossEntry/gls:term[1])">
              <k>
                <xsl:if test="$srcLang != ''">
                  <xsl:attribute name="xml:lang">
                    <xsl:value-of select="$srcLang"/>
                  </xsl:attribute>
                </xsl:if>
                <xsl:value-of select="$srcText"/>
              </k>
            </xsl:if>
          </xsl:when>
          <xsl:otherwise>
            <k>
              <xsl:if test="$srcLang != ''">
                <xsl:attribute name="xml:lang">
                  <xsl:value-of select="$srcLang"/>
                </xsl:attribute>
              </xsl:if>
              <xsl:value-of select="$srcText"/>
            </k>
          </xsl:otherwise>
        </xsl:choose>

        <def>
          <!-- Translation key name as comment -->
          <xsl:if test="@name != ''">
            <co type="id">
              <xsl:text>key: </xsl:text>
              <xsl:value-of select="@name"/>
            </co>
          </xsl:if>

          <!-- Segment state as comment -->
          <xsl:if test="xl:segment/@state and xl:segment/@state != 'final'">
            <co type="state">
              <xsl:value-of select="xl:segment[1]/@state"/>
            </co>
          </xsl:if>

          <!-- Notes -->
          <xsl:for-each select="xl:notes/xl:note">
            <co>
              <xsl:if test="@category != ''">
                <xsl:attribute name="type">
                  <xsl:value-of select="@category"/>
                </xsl:attribute>
              </xsl:if>
              <xsl:value-of select="."/>
            </co>
          </xsl:for-each>

          <!-- Metadata module domains → co -->
          <xsl:for-each select="mda:metadata/mda:metaGroup/mda:meta">
            <co>
              <xsl:attribute name="type">
                <xsl:value-of select="@type"/>
              </xsl:attribute>
              <xsl:value-of select="."/>
            </co>
          </xsl:for-each>

          <!-- Target definition -->
          <xsl:choose>
            <!-- Glossary module translation -->
            <xsl:when test="gls:glossary/gls:glossEntry/gls:translation">
              <deftext>
                <xsl:value-of select="gls:glossary/gls:glossEntry/gls:translation[1]"/>
              </deftext>
            </xsl:when>
            <!-- Segment target -->
            <xsl:when test="normalize-space($trgText) != ''">
              <def>
                <xsl:if test="$trgLang != ''">
                  <xsl:attribute name="xml:lang">
                    <xsl:value-of select="$trgLang"/>
                  </xsl:attribute>
                </xsl:if>
                <deftext>
                  <xsl:value-of select="$trgText"/>
                </deftext>
              </def>
            </xsl:when>
            <xsl:otherwise>
              <deftext/>
            </xsl:otherwise>
          </xsl:choose>

          <!-- Domain metadata as categ -->
          <xsl:for-each select="mda:metadata/mda:metaGroup[@category='domain']/mda:meta">
            <categ>
              <kref><xsl:value-of select="."/></kref>
            </categ>
          </xsl:for-each>

        </def>
      </ar>
    </xsl:if>
  </xsl:template>

</xsl:stylesheet>
