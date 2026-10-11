<?xml version="1.0" encoding="UTF-8"?>
<!--
  flex2xdxf.xsl  —  FLEx Interlinear XML → XDXF rev34

  FLEx Interlinear operates at TEXT level (paragraphs → phrases → words →
  morphemes with glosses), not at dictionary lemma level. This sheet
  collapses interlinear tokens into XDXF entries by grouping on the
  <item type="txt"> (surface form) within each <word> and collecting:
    • type="gls"  → gloss  → deftext
    • type="pos"  → part of speech → gr
    • type="cf"   → citation form → alternate <k>
    • type="msa"  → morphosyntactic analysis → <co>

  Because one surface form may have multiple interlinear analyses, a
  Muenchian grouping key groups all <word> elements by their txt value.
  The first occurrence determines the headword; all glosses are merged.

  FLEx document structure (FlexInterlinear.xsd):
    <document>
      <interlinear-text>
        <languages>
          <language lang="..." font="..." vernacular="true|false"/>
        </languages>
        <paragraphs>
          <paragraph>
            <phrases>
              <phrase>
                <words>
                  <word>
                    <item type="txt" lang="...">surface</item>
                    <item type="gls" lang="...">gloss</item>
                    <item type="pos" lang="...">NOUN</item>
                    <morphemes>
                      <morph type="stem|prefix|suffix">
                        <item type="txt">morph</item>
                        <item type="gls">morph-gloss</item>
                      </morph>
                    </morphemes>
                  </word>
                </words>
                <item type="gls" lang="...">phrase gloss</item>
              </phrase>
            </paragraphs>
          </interlinear-text>
        </paragraphs>
      </interlinear-text>
    </document>
-->
<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output method="xml" encoding="UTF-8" indent="yes"/>
  <xsl:strip-space elements="*"/>

  <!-- Muenchian grouping: one XDXF <ar> per unique txt value -->
  <xsl:key name="words-by-txt" match="word" use="item[@type='txt'][1]"/>

  <!-- ═══════════════════════════════════════════════════════════
       Root
  ═══════════════════════════════════════════════════════════════ -->
  <xsl:template match="/">
    <xsl:apply-templates select="document"/>
  </xsl:template>

  <xsl:template match="document">
    <xdxf revision="34">
      <meta_info>
        <title>
          <xsl:choose>
            <xsl:when test=".//interlinear-text/item[@type='title']">
              <xsl:value-of select=".//interlinear-text/item[@type='title'][1]"/>
            </xsl:when>
            <xsl:otherwise>FLEx Interlinear Export</xsl:otherwise>
          </xsl:choose>
        </title>
        <full_title>
          <xsl:choose>
            <xsl:when test=".//interlinear-text/item[@type='title-abbreviation']">
              <xsl:value-of select=".//interlinear-text/item[@type='title-abbreviation'][1]"/>
            </xsl:when>
            <xsl:otherwise>Converted from FLEx Interlinear by flex2xdxf.xsl</xsl:otherwise>
          </xsl:choose>
        </full_title>
        <description>Converted from FieldWorks Language Explorer interlinear XML</description>

        <languages>
          <!-- Vernacular language = source (<from>) -->
          <xsl:variable name="vernLang"
            select=".//languages/language[@vernacular='true'][1]/@lang"/>
          <from>
            <xsl:attribute name="xml:lang">
              <xsl:choose>
                <xsl:when test="$vernLang != ''">
                  <xsl:value-of select="$vernLang"/>
                </xsl:when>
                <xsl:otherwise>und</xsl:otherwise>
              </xsl:choose>
            </xsl:attribute>
          </from>
          <!-- Analysis languages = targets (<to>) -->
          <xsl:for-each select=".//languages/language[@vernacular='false']">
            <to>
              <xsl:attribute name="xml:lang">
                <xsl:value-of select="@lang"/>
              </xsl:attribute>
            </to>
          </xsl:for-each>
          <!-- Fallback if no vernacular flag -->
          <xsl:if test="not(.//languages/language[@vernacular='true'])">
            <to xml:lang="en"/>
          </xsl:if>
        </languages>

        <file_ver>1.0</file_ver>
        <creation_date/>
        <last_edited_date/>
      </meta_info>

      <lexicon>
        <!-- Muenchian: emit one <ar> per unique surface form -->
        <xsl:for-each select=".//word[
            generate-id(.) = generate-id(key('words-by-txt', item[@type='txt'][1])[1])
          ]">
          <xsl:sort select="item[@type='txt'][1]"/>
          <xsl:call-template name="make-ar"/>
        </xsl:for-each>
      </lexicon>
    </xdxf>
  </xsl:template>

  <!-- ═══════════════════════════════════════════════════════════
       Build one <ar> for a unique surface form
  ═══════════════════════════════════════════════════════════════ -->
  <xsl:template name="make-ar">
    <xsl:variable name="txt"  select="item[@type='txt'][1]"/>
    <xsl:variable name="lang" select="item[@type='txt'][1]/@lang"/>
    <!-- All words in the document sharing this txt -->
    <xsl:variable name="group" select="key('words-by-txt', $txt)"/>

    <ar>
      <!-- Headword -->
      <k>
        <xsl:if test="$lang != ''">
          <xsl:attribute name="xml:lang">
            <xsl:value-of select="$lang"/>
          </xsl:attribute>
        </xsl:if>
        <xsl:value-of select="$txt"/>
      </k>

      <!-- Citation form as alternate headword if different from surface -->
      <xsl:if test="item[@type='cf'] and item[@type='cf'][1] != $txt">
        <k>
          <xsl:if test="$lang != ''">
            <xsl:attribute name="xml:lang">
              <xsl:value-of select="$lang"/>
            </xsl:attribute>
          </xsl:if>
          <xsl:value-of select="item[@type='cf'][1]"/>
        </k>
      </xsl:if>

      <def>
        <!-- Part of speech from first occurrence -->
        <xsl:variable name="pos" select="$group/item[@type='pos'][1]"/>
        <xsl:if test="$pos != ''">
          <gr><xsl:value-of select="$pos"/></gr>
        </xsl:if>

        <!-- Morphosyntactic analysis as comment -->
        <xsl:variable name="msa" select="$group/item[@type='msa'][1]"/>
        <xsl:if test="$msa != ''">
          <co><xsl:value-of select="$msa"/></co>
        </xsl:if>

        <!-- Gloss(es) — collect all unique glosses across group -->
        <xsl:variable name="firstGls" select="$group/item[@type='gls'][1]"/>
        <xsl:choose>
          <xsl:when test="$firstGls != ''">
            <deftext>
              <xsl:value-of select="$firstGls"/>
            </deftext>
            <!-- Additional distinct glosses from other group members -->
            <xsl:for-each select="$group[position() > 1]">
              <xsl:variable name="gls" select="item[@type='gls'][1]"/>
              <xsl:if test="$gls != '' and $gls != $firstGls">
                <deftext><xsl:value-of select="$gls"/></deftext>
              </xsl:if>
            </xsl:for-each>
          </xsl:when>
          <xsl:otherwise>
            <deftext/>
          </xsl:otherwise>
        </xsl:choose>

        <!-- Morpheme breakdowns as etymology note -->
        <xsl:if test="morphemes/morph">
          <etm>
            <xsl:for-each select="morphemes/morph">
              <xsl:value-of select="item[@type='txt']"/>
              <xsl:text>:</xsl:text>
              <xsl:value-of select="item[@type='gls']"/>
              <xsl:if test="position() != last()">
                <xsl:text> + </xsl:text>
              </xsl:if>
            </xsl:for-each>
          </etm>
        </xsl:if>

        <!-- Free translation of the parent phrase as example -->
        <xsl:for-each select="parent::words/parent::phrase">
          <xsl:variable name="ft" select="item[@type='gls'][1]"/>
          <xsl:if test="$ft != ''">
            <ex>
              <ex_orig>
                <xsl:for-each select="words/word/item[@type='txt']">
                  <xsl:value-of select="."/>
                  <xsl:if test="position() != last()">
                    <xsl:text> </xsl:text>
                  </xsl:if>
                </xsl:for-each>
              </ex_orig>
              <ex_tran><xsl:value-of select="$ft"/></ex_tran>
            </ex>
          </xsl:if>
        </xsl:for-each>

      </def>
    </ar>
  </xsl:template>

</xsl:stylesheet>
