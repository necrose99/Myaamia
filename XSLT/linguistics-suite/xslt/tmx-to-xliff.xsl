<?xml version="1.0" encoding="UTF-8"?>
<!--
  tmx-to-xliff.xsl
  Converts TMX 1.4b translation memory to XLIFF 1.2.
  The inverse of xliff-to-tmx.xsl; reconstructs XLIFF file grouping
  from x-xliff-file-original props when available, otherwise produces
  a single XLIFF file containing all TUs.

  Direction : TMX → XLIFF
-->
<xsl:stylesheet
  xmlns:xsl = "http://www.w3.org/1999/XSL/Transform"
  xmlns:its = "http://www.w3.org/2005/11/its"
  version   = "2.0"
  exclude-result-prefixes="its">

  <xsl:output method="xml" encoding="UTF-8" indent="yes"/>
  <xsl:strip-space elements="*"/>

  <xsl:param name="tool-name" select="'tmx-to-xliff.xsl'"/>

  <!-- ============================================================
       Root: TMX → XLIFF
       ============================================================ -->
  <xsl:template match="/tmx">
    <xsl:variable name="src-lang" select="header/@srclang"/>
    <xsl:variable name="admin-lang" select="header/@adminlang"/>

    <xliff version="1.2"
           xmlns="urn:oasis:names:tc:xliff:document:1.2"
           xmlns:its="http://www.w3.org/2005/11/its"
           its:version="1.0">

      <its:rules version="1.0">
        <its:translateRule
          selector="//note[@its:translate='no']"
          translate="no"/>
      </its:rules>

      <!--
        Group TUs by x-xliff-file-original prop.
        If prop is absent, all TUs fall into a synthetic file named "tmx-import".
      -->
      <xsl:for-each-group
        select="body/tu"
        group-by="(prop[@type='x-xliff-file-original'],'tmx-import')[1]">

        <xsl:variable name="file-original" select="current-grouping-key()"/>
        <!-- Determine target lang from first TU's non-source tuv -->
        <xsl:variable name="tgt-lang"
          select="(current-group()/tuv[not(@xml:lang=$src-lang)]/@xml:lang)[1]"/>

        <file xmlns="urn:oasis:names:tc:xliff:document:1.2"
              original        = "{$file-original}"
              source-language = "{$src-lang}"
              target-language = "{$tgt-lang}"
              datatype        = "plaintext"
              its:version="1.0">

          <header xmlns="urn:oasis:names:tc:xliff:document:1.2">
            <tool tool-id="tmx-to-xliff" tool-name="{$tool-name}"/>
            <note>Imported from TMX. Source: <xsl:value-of select="$file-original"/></note>
          </header>

          <body xmlns="urn:oasis:names:tc:xliff:document:1.2">
            <xsl:apply-templates select="current-group()">
              <xsl:with-param name="src-lang" select="$src-lang"/>
              <xsl:with-param name="tgt-lang" select="$tgt-lang"/>
            </xsl:apply-templates>
          </body>
        </file>
      </xsl:for-each-group>
    </xliff>
  </xsl:template>

  <!-- ============================================================
       TMX <tu>  →  XLIFF <trans-unit>
       ============================================================ -->
  <xsl:template match="tu"
                xmlns="urn:oasis:names:tc:xliff:document:1.2">
    <xsl:param name="src-lang"/>
    <xsl:param name="tgt-lang"/>

    <!-- Derive a clean unit id from tuid -->
    <xsl:variable name="unit-id"
                  select="if (@tuid) then @tuid
                          else generate-id()"/>

    <trans-unit id="{$unit-id}">
      <!-- Restore resname from prop if round-tripping from XLIFF -->
      <xsl:if test="prop[@type='x-xliff-resname']">
        <xsl:attribute name="resname"
                       select="prop[@type='x-xliff-resname']"/>
      </xsl:if>

      <source xml:lang="{$src-lang}">
        <xsl:value-of select="tuv[@xml:lang=$src-lang]/seg"/>
      </source>

      <!-- Primary target: first non-source TUV matching target lang -->
      <xsl:variable name="primary-tuv"
        select="tuv[@xml:lang=$tgt-lang]
                    [not(@creationid) or @creationid='primary'][1]"/>
      <xsl:if test="$primary-tuv">
        <target xml:lang="{$tgt-lang}">
          <xsl:value-of select="$primary-tuv/seg"/>
        </target>
      </xsl:if>

      <!-- alt-trans: additional non-source TUVs (alternate suggestions) -->
      <xsl:for-each select="tuv[@xml:lang=$tgt-lang]
                                [not(@creationid='primary')]
                                [position() gt 1]">
        <alt-trans origin="{if (@creationid) then @creationid else 'tmx'}">
          <target xml:lang="{@xml:lang}">
            <xsl:value-of select="seg"/>
          </target>
        </alt-trans>
      </xsl:for-each>

      <!-- Carry x-its-no-translate metadata as XLIFF notes -->
      <xsl:for-each select="prop[@type='x-its-no-translate']">
        <note its:translate="no">
          <xsl:value-of select="."/>
        </note>
      </xsl:for-each>

    </trans-unit>
  </xsl:template>

  <xsl:template match="text()"/>

</xsl:stylesheet>
