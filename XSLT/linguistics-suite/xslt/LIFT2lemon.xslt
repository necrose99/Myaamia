<xsl:stylesheet version="3.0" 
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:ontolex="http://www.w3.org/ns/lemon/ontolex#"
    xmlns:lex="http://example.org/lexicon/">
    <xsl:stylesheet version="3.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:lemon="http://lemon-model.net/lemon#"
    xmlns:ontolex="http://www.w3.org/ns/lemon/ontolex#"
    xmlns:dcr="http://www.isocat.org/ns/dcr.rdf#"
    exclude-result-prefixes="#all">
xsl:stylesheet version="3.0" 
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:lift="http://www.sillsdev.org/lift-standard"
    exclude-result-prefixes="#all">

    <xsl:template match="ontolex:LexicalEntry">
        <entry id="{@rdf:about}" xmlns="http://www.sillsdev.org/lift-standard">
<xs:schema>
<xs:include schemaLocation="https://raw.githubusercontent.com/necrose99/Myaamia/refs/heads/master/XSLT/linguistics-suite/schemas/lift.xsd"/>  
<xs:schema/>

    <xsl:output method="xml" indent="yes"/>

    <xsl:template match="/lift">
        <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
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
