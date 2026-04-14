<xsl:stylesheet version="3.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:lemon="http://lemon-model.net/lemon#"
    xmlns:ontolex="http://www.w3.org/ns/lemon/ontolex#"
    xmlns:dcr="http://www.isocat.org/ns/dcr.rdf#"
    exclude-result-prefixes="#all">
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
