from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

__NAMESPACE__ = "urn:oasis:names:tc:xliff:document:1.2"


class AttrTypeVersion(Enum):
    VALUE_1_2 = "1.2"


@dataclass(kw_only=True)
class Context:
    class Meta:
        name = "context"
        namespace = "urn:oasis:names:tc:xliff:document:1.2"

    context_type: str = field(
        metadata={
            "name": "context-type",
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
class Count:
    class Meta:
        name = "count"
        namespace = "urn:oasis:names:tc:xliff:document:1.2"

    count_type: None | str = field(
        default=None,
        metadata={
            "name": "count-type",
            "type": "Attribute",
        },
    )
    unit: None | str = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    phase_name: None | str = field(
        default=None,
        metadata={
            "name": "phase-name",
            "type": "Attribute",
        },
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
class Glossary:
    class Meta:
        name = "glossary"
        namespace = "urn:oasis:names:tc:xliff:document:1.2"

    internal_file: None | str = field(
        default=None,
        metadata={
            "name": "internal-file",
            "type": "Element",
        },
    )
    external_file: None | Glossary.ExternalFile = field(
        default=None,
        metadata={
            "name": "external-file",
            "type": "Element",
        },
    )

    @dataclass(kw_only=True)
    class ExternalFile:
        uid: None | str = field(
            default=None,
            metadata={
                "type": "Attribute",
            },
        )
        href: str = field(
            metadata={
                "type": "Attribute",
            }
        )


@dataclass(kw_only=True)
class Note:
    class Meta:
        name = "note"
        namespace = "urn:oasis:names:tc:xliff:document:1.2"

    from_value: None | str = field(
        default=None,
        metadata={
            "name": "from",
            "type": "Attribute",
        },
    )
    annotates: None | str = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    priority: None | str = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    other_attributes: dict[str, str] = field(
        default_factory=dict,
        metadata={
            "type": "Attributes",
            "namespace": "##other",
        },
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
class Prop:
    class Meta:
        name = "prop"
        namespace = "urn:oasis:names:tc:xliff:document:1.2"

    prop_type: str = field(
        metadata={
            "name": "prop-type",
            "type": "Attribute",
        }
    )
    lang: None | str = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
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
class Reference:
    class Meta:
        name = "reference"
        namespace = "urn:oasis:names:tc:xliff:document:1.2"

    internal_file: None | str = field(
        default=None,
        metadata={
            "name": "internal-file",
            "type": "Element",
        },
    )
    external_file: None | Reference.ExternalFile = field(
        default=None,
        metadata={
            "name": "external-file",
            "type": "Element",
        },
    )

    @dataclass(kw_only=True)
    class ExternalFile:
        uid: None | str = field(
            default=None,
            metadata={
                "type": "Attribute",
            },
        )
        href: str = field(
            metadata={
                "type": "Attribute",
            }
        )


@dataclass(kw_only=True)
class Skl:
    class Meta:
        name = "skl"
        namespace = "urn:oasis:names:tc:xliff:document:1.2"

    internal_file: None | str = field(
        default=None,
        metadata={
            "name": "internal-file",
            "type": "Element",
        },
    )
    external_file: None | Skl.ExternalFile = field(
        default=None,
        metadata={
            "name": "external-file",
            "type": "Element",
        },
    )

    @dataclass(kw_only=True)
    class ExternalFile:
        uid: None | str = field(
            default=None,
            metadata={
                "type": "Attribute",
            },
        )
        href: str = field(
            metadata={
                "type": "Attribute",
            }
        )


@dataclass(kw_only=True)
class Source:
    class Meta:
        name = "source"
        namespace = "urn:oasis:names:tc:xliff:document:1.2"

    lang: None | str = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
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
class Target:
    class Meta:
        name = "target"
        namespace = "urn:oasis:names:tc:xliff:document:1.2"

    lang: None | str = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    state: None | str = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
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
class Tool:
    class Meta:
        name = "tool"
        namespace = "urn:oasis:names:tc:xliff:document:1.2"

    other_element: list[object] = field(
        default_factory=list,
        metadata={
            "type": "Wildcard",
            "namespace": "##other",
        },
    )
    tool_id: str = field(
        metadata={
            "name": "tool-id",
            "type": "Attribute",
        }
    )
    tool_name: str = field(
        metadata={
            "name": "tool-name",
            "type": "Attribute",
        }
    )
    tool_version: None | str = field(
        default=None,
        metadata={
            "name": "tool-version",
            "type": "Attribute",
        },
    )
    tool_company: None | str = field(
        default=None,
        metadata={
            "name": "tool-company",
            "type": "Attribute",
        },
    )


@dataclass(kw_only=True)
class AltTrans:
    class Meta:
        name = "alt-trans"
        namespace = "urn:oasis:names:tc:xliff:document:1.2"

    source: None | Source = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    target: Target = field(
        metadata={
            "type": "Element",
        }
    )
    note: list[Note] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    match_quality: None | str = field(
        default=None,
        metadata={
            "name": "match-quality",
            "type": "Attribute",
        },
    )
    origin: None | str = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    other_attributes: dict[str, str] = field(
        default_factory=dict,
        metadata={
            "type": "Attributes",
            "namespace": "##other",
        },
    )


@dataclass(kw_only=True)
class BinUnit:
    class Meta:
        name = "bin-unit"
        namespace = "urn:oasis:names:tc:xliff:document:1.2"

    bin_source: BinUnit.BinSource = field(
        metadata={
            "name": "bin-source",
            "type": "Element",
        }
    )
    bin_target: None | BinUnit.BinTarget = field(
        default=None,
        metadata={
            "name": "bin-target",
            "type": "Element",
        },
    )
    note: list[Note] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    id: str = field(
        metadata={
            "type": "Attribute",
        }
    )
    restype: str = field(
        metadata={
            "type": "Attribute",
        }
    )
    mime_type: str = field(
        metadata={
            "name": "mime-type",
            "type": "Attribute",
        }
    )

    @dataclass(kw_only=True)
    class BinSource:
        internal_file: None | str = field(
            default=None,
            metadata={
                "name": "internal-file",
                "type": "Element",
            },
        )
        external_file: None | BinUnit.BinSource.ExternalFile = field(
            default=None,
            metadata={
                "name": "external-file",
                "type": "Element",
            },
        )

        @dataclass(kw_only=True)
        class ExternalFile:
            uid: None | str = field(
                default=None,
                metadata={
                    "type": "Attribute",
                },
            )
            href: str = field(
                metadata={
                    "type": "Attribute",
                }
            )

    @dataclass(kw_only=True)
    class BinTarget:
        internal_file: None | str = field(
            default=None,
            metadata={
                "name": "internal-file",
                "type": "Element",
            },
        )
        external_file: None | BinUnit.BinTarget.ExternalFile = field(
            default=None,
            metadata={
                "name": "external-file",
                "type": "Element",
            },
        )

        @dataclass(kw_only=True)
        class ExternalFile:
            uid: None | str = field(
                default=None,
                metadata={
                    "type": "Attribute",
                },
            )
            href: str = field(
                metadata={
                    "type": "Attribute",
                }
            )


@dataclass(kw_only=True)
class ContextGroup:
    class Meta:
        name = "context-group"
        namespace = "urn:oasis:names:tc:xliff:document:1.2"

    context: list[Context] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "min_occurs": 1,
        },
    )
    name: str = field(
        metadata={
            "type": "Attribute",
        }
    )
    purpose: None | str = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


@dataclass(kw_only=True)
class CountGroup:
    class Meta:
        name = "count-group"
        namespace = "urn:oasis:names:tc:xliff:document:1.2"

    count: list[Count] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "min_occurs": 1,
        },
    )
    name: str = field(
        metadata={
            "type": "Attribute",
        }
    )


@dataclass(kw_only=True)
class Phase:
    class Meta:
        name = "phase"
        namespace = "urn:oasis:names:tc:xliff:document:1.2"

    note: list[Note] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    phase_name: str = field(
        metadata={
            "name": "phase-name",
            "type": "Attribute",
        }
    )
    process_name: str = field(
        metadata={
            "name": "process-name",
            "type": "Attribute",
        }
    )
    tool_id: None | str = field(
        default=None,
        metadata={
            "name": "tool-id",
            "type": "Attribute",
        },
    )
    date: None | str = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    contact_name: None | str = field(
        default=None,
        metadata={
            "name": "contact-name",
            "type": "Attribute",
        },
    )
    contact_email: None | str = field(
        default=None,
        metadata={
            "name": "contact-email",
            "type": "Attribute",
        },
    )


@dataclass(kw_only=True)
class PropGroup:
    class Meta:
        name = "prop-group"
        namespace = "urn:oasis:names:tc:xliff:document:1.2"

    prop: list[Prop] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "min_occurs": 1,
        },
    )
    name: str = field(
        metadata={
            "type": "Attribute",
        }
    )


@dataclass(kw_only=True)
class PhaseGroup:
    class Meta:
        name = "phase-group"
        namespace = "urn:oasis:names:tc:xliff:document:1.2"

    phase: list[Phase] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "min_occurs": 1,
        },
    )


@dataclass(kw_only=True)
class TransUnit:
    class Meta:
        name = "trans-unit"
        namespace = "urn:oasis:names:tc:xliff:document:1.2"

    source: Source = field(
        metadata={
            "type": "Element",
        }
    )
    target: None | Target = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    context_group: list[ContextGroup] = field(
        default_factory=list,
        metadata={
            "name": "context-group",
            "type": "Element",
        },
    )
    count_group: list[CountGroup] = field(
        default_factory=list,
        metadata={
            "name": "count-group",
            "type": "Element",
        },
    )
    note: list[Note] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    prop_group: list[PropGroup] = field(
        default_factory=list,
        metadata={
            "name": "prop-group",
            "type": "Element",
        },
    )
    alt_trans: list[AltTrans] = field(
        default_factory=list,
        metadata={
            "name": "alt-trans",
            "type": "Element",
        },
    )
    id: str = field(
        metadata={
            "type": "Attribute",
        }
    )
    resname: None | str = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    restype: None | str = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    translate: None | str = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    space: None | str = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    other_attributes: dict[str, str] = field(
        default_factory=dict,
        metadata={
            "type": "Attributes",
            "namespace": "##other",
        },
    )


@dataclass(kw_only=True)
class Group:
    class Meta:
        name = "group"
        namespace = "urn:oasis:names:tc:xliff:document:1.2"

    note: list[Note] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    prop_group: list[PropGroup] = field(
        default_factory=list,
        metadata={
            "name": "prop-group",
            "type": "Element",
        },
    )
    count_group: list[CountGroup] = field(
        default_factory=list,
        metadata={
            "name": "count-group",
            "type": "Element",
        },
    )
    trans_unit: list[TransUnit] = field(
        default_factory=list,
        metadata={
            "name": "trans-unit",
            "type": "Element",
        },
    )
    bin_unit: list[BinUnit] = field(
        default_factory=list,
        metadata={
            "name": "bin-unit",
            "type": "Element",
        },
    )
    group: list[Group] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    id: None | str = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    resname: None | str = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    restype: None | str = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    translate: None | str = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    lang: None | str = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    other_attributes: dict[str, str] = field(
        default_factory=dict,
        metadata={
            "type": "Attributes",
            "namespace": "##other",
        },
    )


@dataclass(kw_only=True)
class Header:
    class Meta:
        name = "header"
        namespace = "urn:oasis:names:tc:xliff:document:1.2"

    skl: None | Skl = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    phase_group: None | PhaseGroup = field(
        default=None,
        metadata={
            "name": "phase-group",
            "type": "Element",
        },
    )
    glossary: list[Glossary] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    reference: list[Reference] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    count_group: list[CountGroup] = field(
        default_factory=list,
        metadata={
            "name": "count-group",
            "type": "Element",
        },
    )
    tool: list[Tool] = field(
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
    prop_group: list[PropGroup] = field(
        default_factory=list,
        metadata={
            "name": "prop-group",
            "type": "Element",
        },
    )
    other_element: list[object] = field(
        default_factory=list,
        metadata={
            "type": "Wildcard",
            "namespace": "##other",
        },
    )
    other_attributes: dict[str, str] = field(
        default_factory=dict,
        metadata={
            "type": "Attributes",
            "namespace": "##other",
        },
    )


@dataclass(kw_only=True)
class Body:
    class Meta:
        name = "body"
        namespace = "urn:oasis:names:tc:xliff:document:1.2"

    trans_unit: list[TransUnit] = field(
        default_factory=list,
        metadata={
            "name": "trans-unit",
            "type": "Element",
        },
    )
    bin_unit: list[BinUnit] = field(
        default_factory=list,
        metadata={
            "name": "bin-unit",
            "type": "Element",
        },
    )
    group: list[Group] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )


@dataclass(kw_only=True)
class File:
    class Meta:
        name = "file"
        namespace = "urn:oasis:names:tc:xliff:document:1.2"

    header: None | Header = field(
        default=None,
        metadata={
            "type": "Element",
        },
    )
    body: Body = field(
        metadata={
            "type": "Element",
        }
    )
    original: str = field(
        metadata={
            "type": "Attribute",
        }
    )
    source_language: str = field(
        metadata={
            "name": "source-language",
            "type": "Attribute",
        }
    )
    target_language: None | str = field(
        default=None,
        metadata={
            "name": "target-language",
            "type": "Attribute",
        },
    )
    datatype: str = field(
        metadata={
            "type": "Attribute",
        }
    )
    tool_id: None | str = field(
        default=None,
        metadata={
            "name": "tool-id",
            "type": "Attribute",
        },
    )
    date: None | str = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    category: None | str = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    other_attributes: dict[str, str] = field(
        default_factory=dict,
        metadata={
            "type": "Attributes",
            "namespace": "##other",
        },
    )


@dataclass(kw_only=True)
class Xliff:
    class Meta:
        name = "xliff"
        namespace = "urn:oasis:names:tc:xliff:document:1.2"

    file: list[File] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "min_occurs": 1,
        },
    )
    version: AttrTypeVersion = field(
        metadata={
            "type": "Attribute",
        }
    )
    other_attributes: dict[str, str] = field(
        default_factory=dict,
        metadata={
            "type": "Attributes",
            "namespace": "##other",
        },
    )
