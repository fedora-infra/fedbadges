import inspect
from unittest.mock import Mock, patch

import datanommer
import pytest
from fedora_messaging.config import conf
from tahrir_api import dbapi
from tahrir_api.utils import get_db_manager_from_uri

from fedbadges.cached import configure as configure_cache
from fedbadges.consumer import FedoraBadgesConsumer
from fedbadges.rulesrepo import RulesRepo


@pytest.fixture()
def grep():
    grep_spec = inspect.getfullargspec(datanommer.models.Message.grep)
    print(grep_spec)
    with patch("datanommer.models.Message.grep", spec=grep_spec.args) as patched_grep:
        yield patched_grep


@pytest.fixture()
def fm_config(tmp_path):
    test_config = dict(
        badges_repo="tests/test_badges",
        database_uri=f"sqlite:///{tmp_path.as_posix()}/badges.db",
        datanommer_db_uri=f"sqlite:///{tmp_path.as_posix()}/datanommer.db",
        datagrepper_url="https://example.com/datagrepper",
        distgit_hostname="src.example.com",
        id_provider_hostname="id.example.com",
        fasjson_base_url="https://fasjson.example.com",
        cache=dict(backend="dogpile.cache.null", expiration_time=0),
        badge_issuer=dict(
            issuer_id="test-issuer",
            issuer_name="Testing",
            issuer_origin="http://badges.example.com",
            issuer_url="http://example.com",
            issuer_email="badges@example.com",
        ),
    )
    with patch.dict(conf["consumer_config"], test_config):
        yield


@pytest.fixture()
def notification_callback_mock():
    return Mock(name="notification_callack")


@pytest.fixture()
def badges_db(tmp_path, notification_callback_mock):
    database_uri = f"sqlite:///{tmp_path.as_posix()}/badges.db"
    db = dbapi.TahrirDatabase(
        dburi=database_uri,
        autocommit=False,
        notification_callback=notification_callback_mock,
    )
    db_mgr = get_db_manager_from_uri(database_uri)
    db_mgr.sync()
    yield db
    db.session.rollback()


@pytest.fixture()
def fasjson_client():
    client = Mock(name="fasjson")
    with patch("fedbadges.consumer.fasjson_client.Client", return_value=client):
        yield client


@pytest.fixture()
def consumer(fm_config, badges_db, fasjson_client):
    return FedoraBadgesConsumer()


@pytest.fixture()
def tahrir_client(fm_config, badges_db, notification_callback_mock):
    issuer = conf["consumer_config"]["badge_issuer"]
    badges_db.add_issuer(
        issuer.get("issuer_origin"),
        issuer.get("issuer_name"),
        issuer.get("issuer_url"),
        issuer.get("issuer_email"),
    )
    badges_db.session.commit()
    yield badges_db


@pytest.fixture()
def rules(fm_config, fasjson_client, tahrir_client):
    repo = RulesRepo(conf["consumer_config"], 1, fasjson_client)
    return repo.load_all(tahrir_client=tahrir_client)


@pytest.fixture()
def cache_configured(fm_config):
    cache_args = conf["consumer_config"]["cache"]
    configure_cache(**cache_args)
