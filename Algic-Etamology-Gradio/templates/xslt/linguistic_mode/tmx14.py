from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(kw_only=True)
class Note:
    class Meta:
        name = "note"

    any_attributes: dict[str, str] = field(
        default_factory=dict,
        metadata={
            "type": "Attributes",
            "namespace": "##any",
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

    type_value: str = field(
        metadata={
            "name": "type",
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
class Seg:
    class Meta:
        name = "seg"

    value: str = field(default="")


@dataclass(kw_only=True)
class Ude:
    class Meta:
        name = "ude"

    map: list[Ude.Map] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    name: str = field(
        metadata={
            "type": "Attribute",
        }
    )
    base: None | str = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )

    @dataclass(kw_only=True)
    class Map:
        unicode: str = field(
            metadata={
                "type": "Attribute",
            }
        )
        code: None | str = field(
            default=None,
            metadata={
                "type": "Attribute",
            },
        )
        ent: None | str = field(
            default=None,
            metadata={
                "type": "Attribute",
            },
        )
        subst: None | str = field(
            default=None,
            metadata={
                "type": "Attribute",
            },
        )


@dataclass(kw_only=True)
class Header2:
    class Meta:
        name = "header"

    note: list[Note] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    prop: list[Prop] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    ude: list[Ude] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    creationtool: str = field(
        metadata={
            "type": "Attribute",
        }
    )
    creationtoolversion: str = field(
        metadata={
            "type": "Attribute",
        }
    )
    datatype: str = field(
        metadata={
            "type": "Attribute",
        }
    )
    segtype: str = field(
        metadata={
            "type": "Attribute",
        }
    )
    adminlang: str = field(
        metadata={
            "type": "Attribute",
        }
    )
    srclang: str = field(
        metadata={
            "type": "Attribute",
        }
    )
    creationdate: None | str = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    changedate: None | str = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    creationid: None | str = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    changeid: None | str = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


@dataclass(kw_only=True)
class Tuv:
    class Meta:
        name = "tuv"

    note: list[Note] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    prop: list[Prop] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    seg: Seg = field(
        metadata={
            "type": "Element",
        }
    )
    any_attributes: dict[str, str] = field(
        default_factory=dict,
        metadata={
            "type": "Attributes",
            "namespace": "##any",
        },
    )


@dataclass(kw_only=True)
class Tu:
    class Meta:
        name = "tu"

    note: list[Note] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    prop: list[Prop] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )
    tuv: list[Tuv] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "min_occurs": 2,
        },
    )
    tuid: None | str = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    datatype: None | str = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    usagecount: None | int = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    lastusagedate: None | str = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    creationtool: None | str = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    creationtoolversion: None | str = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    creationdate: None | str = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    creationid: None | str = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    changedate: None | str = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    segtype: None | str = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )
    changeid: None | str = field(
        default=None,
        metadata={
            "type": "Attribute",
        },
    )


@dataclass(kw_only=True)
class Body:
    class Meta:
        name = "body"

    tu: list[Tu] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        },
    )


@dataclass(kw_only=True)
class Tmx:
    class Meta:
        name = "tmx"

    header: Header2 = field(
        metadata={
            "type": "Element",
        }
    )
    body: Body = field(
        metadata={
            "type": "Element",
        }
    )
    version: str = field(
        metadata={
            "type": "Attribute",
        }
    )
