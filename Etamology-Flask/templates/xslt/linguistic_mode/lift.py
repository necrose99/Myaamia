from __future__ import annotations

from dataclasses import dataclass, field

from linguistic_mode.tmx14 import Note


@dataclass(kw_only=True)
class Annotation2:
    class Meta:
        name = "annotation"

    name: str = field(
        metadata={
            "type": "Attribute",
        }
    )
    value: str = field(
        metadata={
            "type": "Attribute",
        }
    )
    who: None | str = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    when: None | str = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


@dataclass(kw_only=True)
class GrammaticalInfo:
    class Meta:
        name = "grammatical-info"

    trait: list[GrammaticalInfo.Trait] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "",
        },
    )
    value: str = field(
        metadata={
            "type": "Attribute",
        }
    )

    @dataclass(kw_only=True)
    class Trait:
        name: str = field(
            metadata={
                "type": "Attribute",
            }
        )
        value: str = field(
            metadata={
                "type": "Attribute",
            }
        )


@dataclass(kw_only=True)
class SemanticDomain:
    class Meta:
        name = "semantic-domain"

    name: str = field(
        metadata={
            "type": "Attribute",
        }
    )


@dataclass(kw_only=True)
class Text:
    class Meta:
        name = "text"

    value: str = field(default="")


@dataclass(kw_only=True)
class Form:
    class Meta:
        name = "form"

    text: None | Text = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    annotation: list[Annotation2] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    lang: str = field(
        metadata={
            "type": "Attribute",
        }
    )


@dataclass(kw_only=True)
class Citation:
    class Meta:
        name = "citation"

    form: list[Form] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "min_occurs": 1,
        },
    )


@dataclass(kw_only=True)
class Definition:
    class Meta:
        name = "definition"

    form: list[Form] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "min_occurs": 1,
        },
    )


@dataclass(kw_only=True)
class FieldType:
    class Meta:
        name = "field"

    form: list[Form] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "min_occurs": 1,
        },
    )
    type_value: str = field(
        metadata={
            "name": "type",
            "type": "Attribute",
        }
    )


@dataclass(kw_only=True)
class Gloss:
    class Meta:
        name = "gloss"

    text: None | Text = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    form: list[Form] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    lang: str = field(
        metadata={
            "type": "Attribute",
        }
    )


@dataclass(kw_only=True)
class Label:
    class Meta:
        name = "label"

    form: list[Form] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "min_occurs": 1,
        },
    )


@dataclass(kw_only=True)
class LexicalUnit:
    class Meta:
        name = "lexical-unit"

    form: list[Form] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "min_occurs": 1,
        },
    )


@dataclass(kw_only=True)
class Main:
    class Meta:
        name = "main"

    form: list[Form] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "min_occurs": 1,
        },
    )
    href: None | str = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


@dataclass(kw_only=True)
class Translation:
    class Meta:
        name = "translation"

    form: list[Form] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "min_occurs": 1,
        },
    )
    type_value: None | str = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
        },
    )


@dataclass(kw_only=True)
class Etymology:
    class Meta:
        name = "etymology"

    form: list[Form] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    gloss: list[Gloss] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    field_value: list[FieldType] = field(
        default_factory=list,
        metadata={
            "name": "field",
            "type": "Element",
        },
    )
    type_value: str = field(
        metadata={
            "name": "type",
            "type": "Attribute",
        }
    )
    source: None | str = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


@dataclass(kw_only=True)
class Example:
    class Meta:
        name = "example"

    form: list[Form] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "min_occurs": 1,
        },
    )
    translation: list[Translation] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    note: list[Note] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    field_value: list[FieldType] = field(
        default_factory=list,
        metadata={
            "name": "field",
            "type": "Element",
        },
    )
    source: None | str = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


@dataclass(kw_only=True)
class Illustration:
    class Meta:
        name = "illustration"

    label: list[Label] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    href: str = field(
        metadata={
            "type": "Attribute",
        }
    )


@dataclass(kw_only=True)
class Media:
    class Meta:
        name = "media"

    label: list[Label] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    href: str = field(
        metadata={
            "type": "Attribute",
        }
    )


@dataclass(kw_only=True)
class Relation:
    class Meta:
        name = "relation"

    field_value: list[FieldType] = field(
        default_factory=list,
        metadata={
            "name": "field",
            "type": "Element",
        },
    )
    type_value: str = field(
        metadata={
            "name": "type",
            "type": "Attribute",
        }
    )
    ref: str = field(
        metadata={
            "type": "Attribute",
        }
    )
    order: None | int = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


@dataclass(kw_only=True)
class Reversal:
    class Meta:
        name = "reversal"

    form: list[Form] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "min_occurs": 1,
        },
    )
    main: None | Main = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    grammatical_info: None | GrammaticalInfo = field(
        default=None,
        metadata={
            "name": "grammatical-info",
            "type": "Element",
        },
    )
    type_value: None | str = field(
        default=None,
        metadata={
            "name": "type",
            "type": "Attribute",
        },
    )


@dataclass(kw_only=True)
class Pronunciation:
    class Meta:
        name = "pronunciation"

    form: list[Form] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "min_occurs": 1,
        },
    )
    media: list[Media] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    field_value: list[FieldType] = field(
        default_factory=list,
        metadata={
            "name": "field",
            "type": "Element",
        },
    )


@dataclass(kw_only=True)
class Subsense:
    class Meta:
        name = "subsense"

    grammatical_info: None | GrammaticalInfo = field(
        default=None,
        metadata={
            "name": "grammatical-info",
            "type": "Element",
        },
    )
    gloss: list[Gloss] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    definition: list[Definition] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    note: list[Note] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    example: list[Example] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    field_value: list[FieldType] = field(
        default_factory=list,
        metadata={
            "name": "field",
            "type": "Element",
        },
    )
    id: None | str = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    order: None | int = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


@dataclass(kw_only=True)
class Sense:
    class Meta:
        name = "sense"

    grammatical_info: None | GrammaticalInfo = field(
        default=None,
        metadata={
            "name": "grammatical-info",
            "type": "Element",
        },
    )
    gloss: list[Gloss] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    definition: list[Definition] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    relation: list[Relation] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    note: list[Note] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    example: list[Example] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    reversal: list[Reversal] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    illustration: list[Illustration] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    subsense: list[Subsense] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    semantic_domain: list[SemanticDomain] = field(
        default_factory=list,
        metadata={
            "name": "semantic-domain",
            "type": "Element",
        },
    )
    field_value: list[FieldType] = field(
        default_factory=list,
        metadata={
            "name": "field",
            "type": "Element",
        },
    )
    id: None | str = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    order: None | int = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


@dataclass(kw_only=True)
class Variant:
    class Meta:
        name = "variant"

    form: list[Form] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "min_occurs": 1,
        },
    )
    relation: list[Relation] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    pronunciation: list[Pronunciation] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    ref: None | str = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


@dataclass(kw_only=True)
class Entry:
    class Meta:
        name = "entry"

    lexical_unit: None | LexicalUnit = field(
        default=None,
        metadata={
            "name": "lexical-unit",
            "type": "Element",
        },
    )
    citation: None | Citation = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    pronunciation: list[Pronunciation] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    variant: list[Variant] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    sense: list[Sense] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    note: list[Note] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    relation: list[Relation] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    etymology: list[Etymology] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    field_value: list[FieldType] = field(
        default_factory=list,
        metadata={
            "name": "field",
            "type": "Element",
        },
    )
    id: str = field(
        metadata={
            "type": "Attribute",
        }
    )
    date_created: None | str = field(
        default=None,
        metadata={
            "name": "dateCreated",
            "type": "Attribute",
        },
    )
    date_modified: None | str = field(
        default=None,
        metadata={
            "name": "dateModified",
            "type": "Attribute",
        },
    )
    morph_type: None | str = field(
        default=None,
        metadata={
            "name": "morph-type",
            "type": "Attribute",
        },
    )
    guid: None | str = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


@dataclass(kw_only=True)
class Lift:
    class Meta:
        name = "lift"

    entry: list[Entry] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    version: str = field(
        metadata={
            "type": "Attribute",
        }
    )
    producer: None | str = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
