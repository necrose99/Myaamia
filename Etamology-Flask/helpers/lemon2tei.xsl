<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="3.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:ontolex="http://www.w3.org/ns/lemon/ontolex#"
    xmlns:lexinfo="http://www.lexinfo.net/ontology/2.0/lexinfo#"
    xmlns:skos="http://www.w3.org/2004/02/skos/core#"
    xmlns:mia="https://mc.miamioh.edu/ilda-myaamia/ontology/ilda#"
    xmlns:tei="http://www.tei-c.org/ns/1.0"
    exclude-result-prefixes="rdf ontolex lexinfo skos mia">

    <xsl:output method="xml" indent="yes" encoding="UTF-8"/>

    <xsl:template match="/rdf:RDF">
        <tei:TEI xmlns:tei="http://www.tei-c.org/ns/1.0">
            <tei:teiHeader>
                <tei:fileDesc>
                    <tei:titleStmt>
                        <tei:title>Myaamia-English TEI Lex-0 Dictionary</tei:title>
                        <tei:respStmt>
                            <tei:resp>Generated from OntoLex-Lemon RDF Graph via XSLT Suite</tei:resp>
                            <tei:name>Myaamia Language Pipeline</tei:name>
                        </tei:respStmt>
                    </tei:titleStmt>
                    <tei:publicationStmt>
                        <tei:p>Published under Myaamia Center / Open Community License</tei:p>
                    </tei:publicationStmt>
                    <tei:sourceDesc>
                        <tei:p>Exported directly from Lemon RDF Graph</tei:p>
                    </tei:sourceDesc>
                </tei:fileDesc>
            </tei:teiHeader>

            <tei:text>
                <tei:body>
                    <tei:entryFree>
                        <xsl:apply-templates select="ontolex:LexicalEntry"/>
                    </tei:entryFree>
                </tei:body>
            </tei:text>
        </tei:TEI>
    </xsl:template>

    <!-- Transform OntoLex Entry to TEI Entry -->
    <xsl:template match="ontolex:LexicalEntry">
        <xsl:variable name="writtenRep" select="ontolex:canonicalForm/ontolex:Form/ontolex:writtenRep/text()"/>
        <xsl:variable name="definition" select="ontolex:sense/ontolex:LexicalSense/skos:definition/text()"/>
        <xsl:variable name="pos" select="lexinfo:partOfSpeech/@rdf:resource"/>

        <tei:entry xml:id="{substring-after(@rdf:about, '#')}">
            <!-- Headword Form -->
            <tei:form type="lemma">
                <tei:orth xml:lang="mia"><xsl:value-of select="$writtenRep"/></tei:orth>
            </tei:form>

            <!-- Part of Speech -->
            <xsl:if test="$pos">
                <tei:gramGrp>
                    <tei:pos><xsl:value-of select="substring-after($pos, '#')"/></tei:pos>
                </tei:gramGrp>
            </xsl:if>

            <!-- Sense and Definition -->
            <xsl:if test="$definition">
                <tei:sense>
                    <tei:def xml:lang="en"><xsl:value-of select="$definition"/></tei:def>
                </tei:sense>
            </xsl:if>
        </tei:entry>
    </xsl:template>

</xsl:stylesheet>
