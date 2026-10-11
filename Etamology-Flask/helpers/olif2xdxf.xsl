<?xml version="1.0" encoding="UTF-8"?>
<!--
  olif2xdxf.xsl  —  OLIF 2.1 → XDXF rev34
  Tested with Saxon-HE 12 and xsltproc (XSLT 1.0 subset).
  XSLT version="1.0" for maximum toolchain compatibility.

  Mapping notes
  ─────────────
  OLIF <entry>   → XDXF <ar>
  <canForm>      → <k xml:lang="…">
  <language>     → xml:lang on <k> (fallback if canForm has no @xml:lang)
  <definition>   → <deftext> inside <def>
  <ptOfSpeech>   → <gr> (grammar label) inside <def>
  <example>      → <ex><ex_orig>
  <note>         → <co> (comment)
  <crossRefer>   → <sr><kref type="…">  (see-also)
  <transfer>     → sibling <ar> records with xml:lang target lang
                   (OLIF bilingual transfer becomes XDXF per-lang defs)
  <subjField>    → <categ> via <kref>
  Gender/number  → appended to <gr>
-->
<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:olif="http://www.olif.net"
    exclude-result-prefixes="olif">

  <xsl:output method="xml" encoding="UTF-8" indent="yes"/>
  <xsl:strip-space elements="*"/>

  <!-- ═══════════════════════════════════════════════════════════
       Root
  ═══════════════════════════════════════════════════════════════ -->
  <xsl:template match="/">
    <xsl:apply-templates select="olif:olif | olif"/>
  </xsl:template>

  <xsl:template match="olif:olif | olif">
    <xdxf revision="34">
      <meta_info>
        <!-- Title from publStmt/distributor/name or fallback -->
        <title>
          <xsl:choose>
            <xsl:when test=".//olif:publStmt/olif:distributor/olif:name ">
              <xsl:value-of select="(.//olif:publStmt/olif:distributor/olif:name)[1]"/>
            </xsl:when>
            <xsl:otherwise>OLIF Dictionary</xsl:otherwise>
          </xsl:choose>
        </title>
        <full_title>
          <xsl:choose>
            <xsl:when test=".//olif:publStmt/olif:distributor/olif:name ">
              <xsl:value-of select="(.//olif:publStmt/olif:distributor/olif:name)[1]"/>
            </xsl:when>
            <xsl:otherwise>Converted from OLIF 2.1</xsl:otherwise>
          </xsl:choose>
        </full_title>
        <description>Converted from OLIF 2.1 by olif2xdxf.xsl</description>
        <languages>
          <!-- Collect unique source language from first entry -->
          <xsl:variable name="srcLang"
            select="(//*[local-name()='entry'][1]/*[local-name()='mono']/*[local-name()='keyDC']/*[local-name()='language'])[1]"/>
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
          <!-- Transfer target languages as <to> elements (best-effort) -->
          <xsl:for-each select=".//*[local-name()='transfer']">
            <xsl:variable name="tgt"
              select="*[local-name()='keyDC']/*[local-name()='language']"/>
            <xsl:if test="$tgt != ''">
              <to>
                <xsl:attribute name="xml:lang">
                  <xsl:value-of select="$tgt"/>
                </xsl:attribute>
              </to>
            </xsl:if>
          </xsl:for-each>
        </languages>
        <file_ver>1.0</file_ver>
        <creation_date>
          <xsl:value-of select="(//*[local-name()='header']/@CreaDate)[1]"/>
        </creation_date>
        <last_edited_date>
          <xsl:value-of select="(//*[local-name()='header']/@CreaDate)[1]"/>
        </last_edited_date>
      </meta_info>

      <lexicon>
        <xsl:apply-templates select=".//olif:entry | .//*[local-name()='entry']"/>
      </lexicon>
    </xdxf>
  </xsl:template>

  <!-- ═══════════════════════════════════════════════════════════
       Each OLIF <entry> becomes one <ar>
  ═══════════════════════════════════════════════════════════════ -->
  <xsl:template match="olif:entry | entry">
    <ar>
      <!-- ── Headword key ── -->
      <xsl:apply-templates select="olif:mono/olif:keyDC "
                           mode="headword"/>

      <!-- ── Definition block ── -->
      <def>
        <!-- Grammar: ptOfSpeech + morphological info -->
        <xsl:variable name="pos"
          select="(olif:mono/olif:keyDC/olif:ptOfSpeech )[1]"/>
        <xsl:variable name="gender"
          select="(olif:mono/olif:monoDC/olif:monoMorph/olif:gender )[1]"/>
        <xsl:variable name="inflect"
          select="(olif:mono/olif:monoDC/olif:monoMorph/olif:inflection )[1]"/>

        <xsl:if test="$pos != '' or $gender != '' or $inflect != ''">
          <gr>
            <xsl:if test="$pos != ''">
              <xsl:value-of select="$pos"/>
            </xsl:if>
            <xsl:if test="$gender != ''">
              <xsl:text> </xsl:text>
              <xsl:value-of select="$gender"/>
            </xsl:if>
            <xsl:if test="$inflect != ''">
              <xsl:text> </xsl:text>
              <xsl:value-of select="$inflect"/>
            </xsl:if>
          </gr>
        </xsl:if>

        <!-- Commentary notes -->
        <xsl:for-each select="olif:mono/olif:generalDC/olif:note ">
          <co><xsl:value-of select="."/></co>
        </xsl:for-each>

        <!-- Definition text -->
        <xsl:choose>
          <xsl:when test="olif:mono/olif:monoDC/olif:monoSem/olif:definition ">
            <deftext>
              <xsl:value-of select="(olif:mono/olif:monoDC/olif:monoSem/olif:definition )[1]"/>
            </deftext>
          </xsl:when>
          <!-- Usage as fallback deftext -->
          <xsl:when test="olif:mono/olif:generalDC/olif:usage ">
            <deftext>
              <xsl:value-of select="(olif:mono/olif:generalDC/olif:usage )[1]"/>
            </deftext>
          </xsl:when>
          <!-- Bilingual transfer targets become language-tagged deftext -->
          <xsl:when test="*[local-name()='transfer']">
            <xsl:apply-templates select="*[local-name()='transfer']"
                                 mode="as-deftext"/>
          </xsl:when>
          <xsl:otherwise>
            <deftext/>
          </xsl:otherwise>
        </xsl:choose>

        <!-- Examples -->
        <xsl:for-each select="olif:mono/olif:generalDC/olif:example ">
          <ex>
            <ex_orig><xsl:value-of select="."/></ex_orig>
          </ex>
        </xsl:for-each>

        <!-- Cross-references → sr/kref -->
        <xsl:if test="*[local-name()='crossRefer']">
          <sr>
            <xsl:apply-templates select="*[local-name()='crossRefer']"
                                 mode="kref"/>
          </sr>
        </xsl:if>

        <!-- Subject field → categ/kref -->
        <xsl:variable name="sf"
          select="(olif:mono/olif:keyDC/olif:subjField )[1]"/>
        <xsl:if test="$sf != '' and $sf != 'general'">
          <categ>
            <kref><xsl:value-of select="$sf"/></kref>
          </categ>
        </xsl:if>
      </def>
    </ar>
  </xsl:template>

  <!-- ═══════════════════════════════════════════════════════════
       Headword <k> from OLIF <keyDC>
  ═══════════════════════════════════════════════════════════════ -->
  <xsl:template match="olif:keyDC | *[local-name()='keyDC' and not(self::olif:keyDC)]" mode="headword">
    <k>
      <xsl:variable name="cfLang"
        select="(*[local-name()='canForm']/@xml:lang)[1]"/>
      <xsl:variable name="langEl"
        select="(*[local-name()='language'])[1]"/>
      <xsl:choose>
        <xsl:when test="$cfLang != ''">
          <xsl:attribute name="xml:lang">
            <xsl:value-of select="$cfLang"/>
          </xsl:attribute>
        </xsl:when>
        <xsl:when test="$langEl != ''">
          <xsl:attribute name="xml:lang">
            <xsl:value-of select="$langEl"/>
          </xsl:attribute>
        </xsl:when>
      </xsl:choose>
      <xsl:value-of select="(*[local-name()='canForm'])[1]"/>
    </k>
  </xsl:template>

  <!-- ═══════════════════════════════════════════════════════════
       OLIF <transfer> → language-tagged <def xml:lang="…">
       (each bilingual transfer pair becomes a nested def)
  ═══════════════════════════════════════════════════════════════ -->
  <xsl:template match="*[local-name()='transfer']" mode="as-deftext">
    <xsl:variable name="tgtLang"
      select="(olif:keyDC/olif:language )[1]"/>
    <xsl:variable name="tgtForm"
      select="(olif:keyDC/olif:canForm )[1]"/>
    <xsl:if test="$tgtForm != ''">
      <def>
        <xsl:if test="$tgtLang != ''">
          <xsl:attribute name="xml:lang">
            <xsl:value-of select="$tgtLang"/>
          </xsl:attribute>
        </xsl:if>
        <deftext><xsl:value-of select="$tgtForm"/></deftext>
      </def>
    </xsl:if>
  </xsl:template>

  <!-- ═══════════════════════════════════════════════════════════
       OLIF <crossRefer> → XDXF <kref>
  ═══════════════════════════════════════════════════════════════ -->
  <xsl:template match="*[local-name()='crossRefer']" mode="kref">
    <xsl:variable name="tgt"  select="@CrTarget"/>
    <xsl:variable name="type" select="(*[local-name()='crLinkType'])[1]"/>
    <kref>
      <xsl:if test="$type != ''">
        <xsl:attribute name="type">
          <xsl:choose>
            <xsl:when test="$type='synonym'">syn</xsl:when>
            <xsl:when test="$type='near-synonym'">syn</xsl:when>
            <xsl:when test="$type='antonym'">ant</xsl:when>
            <xsl:when test="$type='near-antonym'">ant</xsl:when>
            <xsl:when test="$type='has-hyperonym'">hpr</xsl:when>
            <xsl:when test="$type='has-hyponym'">hpn</xsl:when>
            <xsl:when test="$type='has-holonym'">hol</xsl:when>
            <xsl:when test="$type='has-meronym'">mer</xsl:when>
            <xsl:when test="$type='is-derived-from'">etm</xsl:when>
            <xsl:otherwise>rel</xsl:otherwise>
          </xsl:choose>
        </xsl:attribute>
      </xsl:if>
      <xsl:value-of select="$tgt"/>
    </kref>
  </xsl:template>

</xsl:stylesheet>
