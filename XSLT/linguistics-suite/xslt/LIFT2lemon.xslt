<xsl:stylesheet version="3.0" 
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:ontolex="http://www.w3.org/ns/lemon/ontolex#"
    xmlns:lemon="http://lemon-model.net/lemon#"
    xmlns:skos="http://www.w3.org/2004/02/skos/core#"
    xmlns:lift="http://www.sillsdev.org/lift-standard"
    exclude-result-prefixes="lift">

    <xsl:output method="xml" indent="yes" encoding="UTF-8"/>

    <xsl:template match="/lift">
        <rdf:RDF>
            <xsl:apply-templates select="entry"/>
        </rdf:RDF>
    </xsl:template>

    <xsl:template match="entry">
        <ontolex:LexicalEntry rdf:about="{concat('lex:', @id)}">
            <ontolex:canonicalForm>
                <ontolex:Form>
                    <ontolex:writtenRep xml:lang="{lexical-unit/form/@lang}">
                        <xsl:value-of select="lexical-unit/form/text"/>
                    </ontolex:writtenRep>
                </ontolex:Form>
            </ontolex:canonicalForm>
            
            <xsl:if test="etymology">
                <lemon:etymology>
                    <xsl:value-of select="etymology/form/text"/>
                </lemon:etymology>
            </xsl:if>

            <xsl:for-each select="sense">
                <ontolex:sense>
                    <ontolex:LexicalSense rdf:about="{concat('lex:', ../@id, '_sense_', position())}">
                        <xsl:for-each select="gloss">
                            <skos:definition xml:lang="{@lang}">
                                <xsl:value-of select="text"/>
                            </skos:definition>
                        </xsl:for-each>
                    </ontolex:LexicalSense>
                </ontolex:sense>
            </xsl:for-each>
        </ontolex:LexicalEntry>
    </xsl:template>
</xsl:stylesheet>
