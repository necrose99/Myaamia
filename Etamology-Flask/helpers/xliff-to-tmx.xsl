<?xml version="1.0" encoding="UTF-8"?>
<!--
  xliff-to-tmx.xsl
  Converts XLIFF 1.2 translation units directly to TMX 1.4b.
  This is the "bridge" direction in the multi-directional graph,
  allowing CAT-tool XLIFF output to feed a translation memory
  without requiring an intermediate LIFT round-trip.

  Direction : XLIFF → TMX

  ITS its:translate="no" notes are carried forward as TMX
  <prop type="x-its-no-translate"> markers so downstream tools
  can suppress re-translation of grammatical metadata.
-->
<xsl:stylesheet
  xmlns:xsl = "http://www.w3.org/1999/XSL/Transform"
  xmlns:xl  = "urn:oasis:names:tc:xliff:document:1.2"
  xmlns:its = "http://www.w3.org/2005/11/its"
  version   = "2.0"
  exclude-result-prefixes="xl its">

  <xsl:output method="xml" encoding="UTF-8" indent="yes"/>
  <xsl:strip-space elements="*"/>

  <xsl:param name="creationtool"  select="'xliff-to-tmx.xsl'"/>
  <xsl:param name="creationdate"  select="string(current-dateTime())"/>
  <xsl:param name="datatype"      select="'PlainText'"/>

  <!-- ============================================================
       Root: XLIFF → TMX
       ============================================================ -->
  <xsl:template match="/xl:xliff">
    <!-- Derive srclang from first file element -->
    <xsl:variable name="src-lang"
                  select="(xl:file/@source-language)[1]"/>
    <xsl:variable name="admin-lang"
                  select="(xl:file/@target-language,'en')[1]"/>

    <tmx version="1.4">
      <header
        creationtool        = "{$creationtool}"
        creationtoolversion = "1.0"
        datatype            = "{$datatype}"
        segtype             = "sentence"
        adminlang           = "{$admin-lang}"
        srclang             = "{$src-lang}"
        creationdate        = "{$creationdate}">
        <note xml:lang="{$admin-lang}">
          Produced from XLIFF 1.2 by xliff-to-tmx.xsl.
          ITS translate="no" segments preserved as x-its-no-translate props.
        </note>
      </header>

      <body>
        <!--
          Only emit TUs for trans-units that have BOTH a source
          and a non-empty target — i.e. actually translated segments.
          Skip units with its:translate="no" (metadata rows).
        -->
        <xsl:apply-templates
          select="//xl:trans-unit[xl:target[normalize-space(.)!='']
                                  and not(@its:translate='no')]"/>
      </body>
    </tmx>
  </xsl:template>

  <!-- ============================================================
       XLIFF <trans-unit>  →  TMX <tu>
       ============================================================ -->
  <xsl:template match="xl:trans-unit">
    <xsl:variable name="file"     select="ancestor::xl:file"/>
    <xsl:variable name="src-lang" select="$file/@source-language"/>
    <xsl:variable name="tgt-lang" select="$file/@target-language"/>
    <xsl:variable name="tu-id"    select="concat($file/@original,'.',@id)"/>

    <tu tuid     = "{$tu-id}"
        datatype = "{$datatype}"
        creationdate="{$creationdate}">

      <!-- Preserve resname as TMX prop for round-trip context -->
      <xsl:if test="@resname">
        <prop type="x-xliff-resname">
          <xsl:value-of select="@resname"/>
        </prop>
      </xsl:if>
      <!-- Carry file/@original as provenance -->
      <prop type="x-xliff-file-original">
        <xsl:value-of select="$file/@original"/>
      </prop>

      <!-- Carry notes that were marked its:translate="no" -->
      <xsl:for-each select="ancestor::xl:group/xl:note[@its:translate='no']
                            | ancestor::xl:file/xl:header/xl:note[@its:translate='no']">
        <prop type="x-its-no-translate">
          <xsl:value-of select="normalize-space(.)"/>
        </prop>
      </xsl:for-each>

      <!-- alt-trans as additional TMX <tuv> variants -->
      <xsl:variable name="has-alt"
                    select="exists(xl:alt-trans[xl:target])"/>

      <tuv xml:lang="{$src-lang}">
        <seg><xsl:apply-templates select="xl:source" mode="inline"/></seg>
      </tuv>

      <tuv xml:lang="{$tgt-lang}">
        <xsl:if test="$has-alt">
          <xsl:attribute name="creationid">primary</xsl:attribute>
        </xsl:if>
        <seg><xsl:apply-templates select="xl:target" mode="inline"/></seg>
      </tuv>

      <!-- alt-trans become additional tuv entries with changeid markers -->
      <xsl:for-each select="xl:alt-trans[xl:target]">
        <tuv xml:lang="{xl:target/@xml:lang}">
          <xsl:attribute name="creationid">
            <xsl:value-of
              select="concat('alt-',if(@origin) then @origin else position())"/>
          </xsl:attribute>
          <xsl:if test="@match-quality">
            <xsl:attribute name="changedate">
              <xsl:value-of select="$creationdate"/>
            </xsl:attribute>
          </xsl:if>
          <seg><xsl:apply-templates select="xl:target" mode="inline"/></seg>
        </tuv>
      </xsl:for-each>
    </tu>
  </xsl:template>

  <!-- ============================================================
       Inline content: strip XLIFF inline tags, keep text
       (XLIFF <g>, <ph>, <x/> → TMX plain text or <hi>)
       ============================================================ -->
  <xsl:template match="xl:source | xl:target" mode="inline">
    <xsl:apply-templates mode="inline"/>
  </xsl:template>

  <!-- XLIFF <g> (grouped inline) → TMX <hi> with type annotation -->
  <xsl:template match="xl:g" mode="inline">
    <hi type="{if (@ctype) then @ctype else 'x-g'}">
      <xsl:apply-templates mode="inline"/>
    </hi>
  </xsl:template>

  <!-- XLIFF <ph> (placeholder) → strip but preserve content -->
  <xsl:template match="xl:ph" mode="inline">
    <xsl:apply-templates mode="inline"/>
  </xsl:template>

  <!-- XLIFF <x/> (standalone placeholder) → suppress -->
  <xsl:template match="xl:x" mode="inline"/>

  <!-- Plain text pass-through -->
  <xsl:template match="text()" mode="inline">
    <xsl:value-of select="."/>
  </xsl:template>

  <xsl:template match="text()"/>

</xsl:stylesheet>
