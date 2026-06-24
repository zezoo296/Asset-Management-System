from ast import Import
import enum


class AssetType(str, enum.Enum):
    DOMAIN = "domain"
    SUBDOMAIN = "subdomain"
    IP_ADDRESS = "ip_address"
    SERVICE = "service"
    CERTIFICATE = "certificate"
    TECHNOLOGY = "technology"

class AssetSource(str, enum.Enum):
    IMPORT = "import"
    SCAN = "scan"
    MANUAL = "manual"


class AssetStatus(str, enum.Enum):
    ACTIVE = "active"
    STALE = "stale"
    ARCHIVED = "archived"


class RelationType(str, enum.Enum):
    PARENT = "parent"
    COVERS = "covers"
    DETECTED_ON = "detected_on"
    RESOLVES_TO = "resolves_to"
    Resolved_FROM = "resolved_from"
    RUNS_ON = "runs_on"