from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(kw_only=True)
class AnnotationAttribute:
    class Meta:
        name = "ANNOTATION_ATTRIBUTE"

    name: str = field(
        metadata={
            "name": "NAME",
            "type": "Attribute",
        }
    )
    value: str = field(
        metadata={
            "name": "VALUE",
            "type": "Attribute",
        }
    )


@dataclass(kw_only=True)
class AnnotationValue:
    class Meta:
        name = "ANNOTATION_VALUE"

    value: str = field(default="")


@dataclass(kw_only=True)
class Constraint:
    class Meta:
        name = "CONSTRAINT"

    description: None | str = field(
        default=None,
        metadata={
            "name": "DESCRIPTION",
            "type": "Attribute",
        },
    )
    stereotype: str = field(
        metadata={
            "name": "STEREOTYPE",
            "type": "Attribute",
        }
    )


@dataclass(kw_only=True)
class ControlledVocabulary:
    class Meta:
        name = "CONTROLLED_VOCABULARY"

    description: list[ControlledVocabulary.Description] = field(
        default_factory=list,
        metadata={
            "name": "DESCRIPTION",
            "type": "Element",
            "namespace": "",
        },
    )
    cv_entry_ml: list[ControlledVocabulary.CvEntryMl] = field(
        default_factory=list,
        metadata={
            "name": "CV_ENTRY_ML",
            "type": "Element",
            "namespace": "",
        },
    )
    cv_id: str = field(
        metadata={
            "name": "CV_ID",
            "type": "Attribute",
        }
    )
    ext_ref: None | str = field(
        default=None,
        metadata={
            "name": "EXT_REF",
            "type": "Attribute",
        },
    )

    @dataclass(kw_only=True)
    class Description:
        lang_ref: str = field(
            metadata={
                "name": "LANG_REF",
                "type": "Attribute",
            }
        )
        content: list[object] = field(
            default_factory=list,
            metadata={
                "type": "Wildcard",
                "namespace": "##any",
                "mixed": True,
            },
        )

    @dataclass(kw_only=True)
    class CvEntryMl:
        cve_value: list[ControlledVocabulary.CvEntryMl.CveValue] = field(
            default_factory=list,
            metadata={
                "name": "CVE_VALUE",
                "type": "Element",
                "namespace": "",
                "min_occurs": 1,
            },
        )
        cve_id: str = field(
            metadata={
                "name": "CVE_ID",
                "type": "Attribute",
            }
        )
        ext_ref: None | str = field(
            default=None,
            metadata={
                "name": "EXT_REF",
                "type": "Attribute",
            },
        )

        @dataclass(kw_only=True)
        class CveValue:
            description: None | str = field(
                default=None,
                metadata={
                    "name": "DESCRIPTION",
                    "type": "Attribute",
                },
            )
            lang_ref: str = field(
                metadata={
                    "name": "LANG_REF",
                    "type": "Attribute",
                }
            )
            content: list[object] = field(
                default_factory=list,
                metadata={
                    "type": "Wildcard",
                    "namespace": "##any",
                    "mixed": True,
                },
            )


@dataclass(kw_only=True)
class ExternalRef:
    class Meta:
        name = "EXTERNAL_REF"

    ext_ref_id: str = field(
        metadata={
            "name": "EXT_REF_ID",
            "type": "Attribute",
        }
    )
    type_value: str = field(
        metadata={
            "name": "TYPE",
            "type": "Attribute",
        }
    )
    value: str = field(
        metadata={
            "name": "VALUE",
            "type": "Attribute",
        }
    )


@dataclass(kw_only=True)
class Language:
    class Meta:
        name = "LANGUAGE"

    lang_id: str = field(
        metadata={
            "name": "LANG_ID",
            "type": "Attribute",
        }
    )
    lang_def: None | str = field(
        default=None,
        metadata={
            "name": "LANG_DEF",
            "type": "Attribute",
        },
    )
    lang_label: None | str = field(
        default=None,
        metadata={
            "name": "LANG_LABEL",
            "type": "Attribute",
        },
    )


@dataclass(kw_only=True)
class LexiconRef:
    class Meta:
        name = "LEXICON_REF"

    lrid: str = field(
        metadata={
            "name": "LRID",
            "type": "Attribute",
        }
    )
    name: str = field(
        metadata={
            "name": "NAME",
            "type": "Attribute",
        }
    )
    type_value: str = field(
        metadata={
            "name": "TYPE",
            "type": "Attribute",
        }
    )
    url: str = field(
        metadata={
            "name": "URL",
            "type": "Attribute",
        }
    )
    lexicon_id: str = field(
        metadata={
            "name": "LEXICON_ID",
            "type": "Attribute",
        }
    )
    lexicon_name: str = field(
        metadata={
            "name": "LEXICON_NAME",
            "type": "Attribute",
        }
    )
    datcat_id: None | str = field(
        default=None,
        metadata={
            "name": "DATCAT_ID",
            "type": "Attribute",
        },
    )
    datcat_name: None | str = field(
        default=None,
        metadata={
            "name": "DATCAT_NAME",
            "type": "Attribute",
        },
    )


@dataclass(kw_only=True)
class LinguisticType:
    class Meta:
        name = "LINGUISTIC_TYPE"

    linguistic_type_id: str = field(
        metadata={
            "name": "LINGUISTIC_TYPE_ID",
            "type": "Attribute",
        }
    )
    time_alignable: bool = field(
        metadata={
            "name": "TIME_ALIGNABLE",
            "type": "Attribute",
        }
    )
    constraints: None | str = field(
        default=None,
        metadata={
            "name": "CONSTRAINTS",
            "type": "Attribute",
        },
    )
    graphic_references: bool = field(
        metadata={
            "name": "GRAPHIC_REFERENCES",
            "type": "Attribute",
        }
    )
    controlled_vocabulary_ref: None | str = field(
        default=None,
        metadata={
            "name": "CONTROLLED_VOCABULARY_REF",
            "type": "Attribute",
        },
    )
    ext_ref: None | str = field(
        default=None,
        metadata={
            "name": "EXT_REF",
            "type": "Attribute",
        },
    )
    lexicon_ref: None | str = field(
        default=None,
        metadata={
            "name": "LEXICON_REF",
            "type": "Attribute",
        },
    )


@dataclass(kw_only=True)
class LinkedFileDescriptor:
    class Meta:
        name = "LINKED_FILE_DESCRIPTOR"

    link_url: str = field(
        metadata={
            "name": "LINK_URL",
            "type": "Attribute",
        }
    )
    relative_link_url: None | str = field(
        default=None,
        metadata={
            "name": "RELATIVE_LINK_URL",
            "type": "Attribute",
        },
    )
    mime_type: str = field(
        metadata={
            "name": "MIME_TYPE",
            "type": "Attribute",
        }
    )
    time_origin: None | int = field(
        default=None,
        metadata={
            "name": "TIME_ORIGIN",
            "type": "Attribute",
        },
    )
    associated_with: None | str = field(
        default=None,
        metadata={
            "name": "ASSOCIATED_WITH",
            "type": "Attribute",
        },
    )


@dataclass(kw_only=True)
class Locale:
    class Meta:
        name = "LOCALE"

    language_code: str = field(
        metadata={
            "name": "LANGUAGE_CODE",
            "type": "Attribute",
        }
    )
    country_code: None | str = field(
        default=None,
        metadata={
            "name": "COUNTRY_CODE",
            "type": "Attribute",
        },
    )
    variant: None | str = field(
        default=None,
        metadata={
            "name": "VARIANT",
            "type": "Attribute",
        },
    )


@dataclass(kw_only=True)
class MediaDescriptor:
    class Meta:
        name = "MEDIA_DESCRIPTOR"

    media_url: str = field(
        metadata={
            "name": "MEDIA_URL",
            "type": "Attribute",
        }
    )
    mime_type: str = field(
        metadata={
            "name": "MIME_TYPE",
            "type": "Attribute",
        }
    )
    relative_media_url: None | str = field(
        default=None,
        metadata={
            "name": "RELATIVE_MEDIA_URL",
            "type": "Attribute",
        },
    )
    time_origin: None | int = field(
        default=None,
        metadata={
            "name": "TIME_ORIGIN",
            "type": "Attribute",
        },
    )
    extracted_from: None | str = field(
        default=None,
        metadata={
            "name": "EXTRACTED_FROM",
            "type": "Attribute",
        },
    )


@dataclass(kw_only=True)
class Property:
    class Meta:
        name = "PROPERTY"

    name: str = field(
        metadata={
            "name": "NAME",
            "type": "Attribute",
        }
    )
    content: list[object] = field(
        default_factory=list,
        metadata={
            "type": "Wildcard",
            "namespace": "##any",
            "mixed": True,
        },
    )


@dataclass(kw_only=True)
class TimeSlot:
    class Meta:
        name = "TIME_SLOT"

    time_slot_id: str = field(
        metadata={
            "name": "TIME_SLOT_ID",
            "type": "Attribute",
        }
    )
    time_value: None | int = field(
        default=None,
        metadata={
            "name": "TIME_VALUE",
            "type": "Attribute",
        },
    )


@dataclass(kw_only=True)
class AlignableAnnotation:
    class Meta:
        name = "ALIGNABLE_ANNOTATION"

    annotation_value: AnnotationValue = field(
        metadata={
            "name": "ANNOTATION_VALUE",
            "type": "Element",
        }
    )
    annotation_attribute: list[AnnotationAttribute] = field(
        default_factory=list,
        metadata={
            "name": "ANNOTATION_ATTRIBUTE",
            "type": "Element",
        },
    )
    annotation_id: str = field(
        metadata={
            "name": "ANNOTATION_ID",
            "type": "Attribute",
        }
    )
    time_slot_ref1: str = field(
        metadata={
            "name": "TIME_SLOT_REF1",
            "type": "Attribute",
        }
    )
    time_slot_ref2: str = field(
        metadata={
            "name": "TIME_SLOT_REF2",
            "type": "Attribute",
        }
    )
    svg_ref: None | str = field(
        default=None,
        metadata={
            "name": "SVG_REF",
            "type": "Attribute",
        },
    )
    ext_ref: None | str = field(
        default=None,
        metadata={
            "name": "EXT_REF",
            "type": "Attribute",
        },
    )


@dataclass(kw_only=True)
class Header1:
    class Meta:
        name = "HEADER"

    media_descriptor: list[MediaDescriptor] = field(
        default_factory=list,
        metadata={
            "name": "MEDIA_DESCRIPTOR",
            "type": "Element",
        },
    )
    linked_file_descriptor: list[LinkedFileDescriptor] = field(
        default_factory=list,
        metadata={
            "name": "LINKED_FILE_DESCRIPTOR",
            "type": "Element",
        },
    )
    property: list[Property] = field(
        default_factory=list,
        metadata={
            "name": "PROPERTY",
            "type": "Element",
        },
    )
    media_file: str = field(
        metadata={
            "name": "MEDIA_FILE",
            "type": "Attribute",
        }
    )
    time_units: str = field(
        metadata={
            "name": "TIME_UNITS",
            "type": "Attribute",
        }
    )


@dataclass(kw_only=True)
class RefAnnotation:
    class Meta:
        name = "REF_ANNOTATION"

    annotation_value: AnnotationValue = field(
        metadata={
            "name": "ANNOTATION_VALUE",
            "type": "Element",
        }
    )
    annotation_attribute: list[AnnotationAttribute] = field(
        default_factory=list,
        metadata={
            "name": "ANNOTATION_ATTRIBUTE",
            "type": "Element",
        },
    )
    annotation_id: str = field(
        metadata={
            "name": "ANNOTATION_ID",
            "type": "Attribute",
        }
    )
    annotation_ref: str = field(
        metadata={
            "name": "ANNOTATION_REF",
            "type": "Attribute",
        }
    )
    cve_ref: None | str = field(
        default=None,
        metadata={
            "name": "CVE_REF",
            "type": "Attribute",
        },
    )
    ext_ref: None | str = field(
        default=None,
        metadata={
            "name": "EXT_REF",
            "type": "Attribute",
        },
    )


@dataclass(kw_only=True)
class TimeOrder:
    class Meta:
        name = "TIME_ORDER"

    time_slot: list[TimeSlot] = field(
        default_factory=list,
        metadata={
            "name": "TIME_SLOT",
            "type": "Element",
        },
    )


@dataclass(kw_only=True)
class Annotation1:
    class Meta:
        name = "ANNOTATION"

    alignable_annotation: None | AlignableAnnotation = field(
        default=None,
        metadata={
            "name": "ALIGNABLE_ANNOTATION",
            "type": "Element",
        },
    )
    ref_annotation: None | RefAnnotation = field(
        default=None,
        metadata={
            "name": "REF_ANNOTATION",
            "type": "Element",
        },
    )


@dataclass(kw_only=True)
class Tier:
    class Meta:
        name = "TIER"

    annotation: list[Annotation1] = field(
        default_factory=list,
        metadata={
            "name": "ANNOTATION",
            "type": "Element",
        },
    )
    tier_id: str = field(
        metadata={
            "name": "TIER_ID",
            "type": "Attribute",
        }
    )
    participant: None | str = field(
        default=None,
        metadata={
            "name": "PARTICIPANT",
            "type": "Attribute",
        },
    )
    annotator: None | str = field(
        default=None,
        metadata={
            "name": "ANNOTATOR",
            "type": "Attribute",
        },
    )
    linguistic_type_ref: str = field(
        metadata={
            "name": "LINGUISTIC_TYPE_REF",
            "type": "Attribute",
        }
    )
    default_locale: None | str = field(
        default=None,
        metadata={
            "name": "DEFAULT_LOCALE",
            "type": "Attribute",
        },
    )
    parent_ref: None | str = field(
        default=None,
        metadata={
            "name": "PARENT_REF",
            "type": "Attribute",
        },
    )
    lang_ref: None | str = field(
        default=None,
        metadata={
            "name": "LANG_REF",
            "type": "Attribute",
        },
    )
    ext_ref: None | str = field(
        default=None,
        metadata={
            "name": "EXT_REF",
            "type": "Attribute",
        },
    )


@dataclass(kw_only=True)
class AnnotationDocument:
    class Meta:
        name = "ANNOTATION_DOCUMENT"

    header: Header1 = field(
        metadata={
            "name": "HEADER",
            "type": "Element",
        }
    )
    time_order: TimeOrder = field(
        metadata={
            "name": "TIME_ORDER",
            "type": "Element",
        }
    )
    tier: list[Tier] = field(
        default_factory=list,
        metadata={
            "name": "TIER",
            "type": "Element",
        },
    )
    linguistic_type: list[LinguisticType] = field(
        default_factory=list,
        metadata={
            "name": "LINGUISTIC_TYPE",
            "type": "Element",
        },
    )
    locale: list[Locale] = field(
        default_factory=list,
        metadata={
            "name": "LOCALE",
            "type": "Element",
        },
    )
    language: list[Language] = field(
        default_factory=list,
        metadata={
            "name": "LANGUAGE",
            "type": "Element",
        },
    )
    constraint: list[Constraint] = field(
        default_factory=list,
        metadata={
            "name": "CONSTRAINT",
            "type": "Element",
        },
    )
    controlled_vocabulary: list[ControlledVocabulary] = field(
        default_factory=list,
        metadata={
            "name": "CONTROLLED_VOCABULARY",
            "type": "Element",
        },
    )
    lexicon_ref: list[LexiconRef] = field(
        default_factory=list,
        metadata={
            "name": "LEXICON_REF",
            "type": "Element",
        },
    )
    external_ref: list[ExternalRef] = field(
        default_factory=list,
        metadata={
            "name": "EXTERNAL_REF",
            "type": "Element",
        },
    )
    author: str = field(
        metadata={
            "name": "AUTHOR",
            "type": "Attribute",
        }
    )
    date: str = field(
        metadata={
            "name": "DATE",
            "type": "Attribute",
        }
    )
    format: str = field(
        metadata={
            "name": "FORMAT",
            "type": "Attribute",
        }
    )
    version: str = field(
        metadata={
            "name": "VERSION",
            "type": "Attribute",
        }
    )
