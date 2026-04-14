<xsl:stylesheet version="3.0" 
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:ontolex="http://www.w3.org/ns/lemon/ontolex#"
    xmlns:lemon="http://lemon-model.net/lemon#"
    xmlns:skos="http://www.w3.org/2004/02/skos/core#"
    xmlns:lift="http://www.sillsdev.org/lift-standard"
    exclude-result-prefixes="#all">

    <xsl:output method="xml" indent="yes" encoding="UTF-8"/>

    <xsl:template match="/lift">
        <rdf:RDF>
            <xsl:apply-templates select="entry" mode="to-lemon"/>
        </rdf:RDF>
    </xsl:template>

    <xsl:template match="entry" mode="to-lemon">
        <ontolex:LexicalEntry rdf:about="{concat('lex:', @id)}">
            <ontolex:canonicalForm>
                <ontolex:Form>
                    <ontolex:writtenRep xml:lang="{lexical-unit/form/@lang}">
                        <xsl:value-of select="lexical-unit/form/text"/>
                    </ontolex:writtenRep>
                </ontolex:Form>
            </ontolex:canonicalForm>
            
            <xsl:for-each select="trait">
                <lemon:property rdf:resource="{concat('http://isocat.org/datcat/', @name)}" lemon:value="{@value}"/>
            </xsl:for-each>

            <xsl:apply-templates select="sense" mode="to-lemon"/>
        </ontolex:LexicalEntry>
    </xsl:template>

    <xsl:template match="sense" mode="to-lemon">
        <ontolex:sense>
            <ontolex:LexicalSense rdf:about="{concat('lex:', ../@id, '_sense_', position())}">
                <xsl:for-each select="gloss">
                    <skos:definition xml:lang="{@lang}"><xsl:value-of select="text"/></skos:definition>
                </xsl:for-each>
            </ontolex:LexicalSense>
        </ontolex:sense>
    </xsl:template>

    <xsl:template match="ontolex:LexicalEntry" mode="to-lift">
        <entry id="{substring-after(@rdf:about, 'lex:')}" xmlns="http://www.sillsdev.org/lift-standard">
            <lexical-unit>
                <form lang="{ontolex:canonicalForm/ontolex:Form/ontolex:writtenRep/@xml:lang}">
                    <text><xsl:value-of select="ontolex:canonicalForm/ontolex:Form/ontolex:writtenRep"/></text>
                </form>
            </lexical-unit>
            <xsl:apply-templates select="ontolex:sense/ontolex:LexicalSense" mode="to-lift"/>
        </entry>
    </xsl:template>
</xsl:stylesheet>
