<xsl:template match="ontolex:LexicalEntry">
    <entry id="{substring-after(@rdf:about, 'lex:')}">
        <lexical-unit>
            <form lang="{ontolex:canonicalForm/ontolex:Form/ontolex:writtenRep/@xml:lang}">
                <text><xsl:value-of select="ontolex:canonicalForm/ontolex:Form/ontolex:writtenRep"/></text>
            </form>
        </lexical-unit>
        <xsl:for-each select="ontolex:sense/ontolex:LexicalSense">
            <sense id="{@rdf:about}">
                <xsl:for-each select="skos:definition">
                    <gloss lang="{@xml:lang}">
                        <text><xsl:value-of select="."/></text>
                    </gloss>
                </xsl:for-each>
            </sense>
        </xsl:for-each>
    </entry>
</xsl:template>
