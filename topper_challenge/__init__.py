from pyramid.config import Configurator
from ramses import registry
import requests,json

def main(global_config, **settings):
    config = Configurator(settings=settings)
    config.include('ramses')
    return config.make_wsgi_app()

@registry.add
def get_battle_stats(event):
    params={}
    params["_aggregations.most_active_attacker_king.terms.field"]="attacker_king.untouched"
    params["_aggregations.most_active_defender_king.terms.field"] = "defender_king.untouched"
    params["_aggregations.most_active_region.terms.field"] = "region.untouched"
    params["_aggregations.attacker_outcome.terms.field"] = "attacker_outcome"
    params["_aggregations.defender_size.stats.field"] = "defender_size"
    params["_aggregations.battle_type.terms.field"]= "battle_type.untouched"
    resource = requests.get('http://127.0.0.1:6543/api/battles',params=params)
    resource_data = json.loads(resource.content)
    if not resource.status_code ==200:
        raise Exception("Please try after some time")
    stats = {}
    most_active={}
    if resource_data["most_active_attacker_king"]["buckets"].__len__()>0:
        most_active["attacker_king"] = resource_data["most_active_attacker_king"]["buckets"][0]["key"]
    if resource_data["most_active_defender_king"]["buckets"].__len__()>0:
        most_active["defender_king"] = resource_data["most_active_defender_king"]["buckets"][0]["key"]
    if resource_data["most_active_region"]["buckets"].__len__()>0:
        most_active["region"] = resource_data["most_active_region"]["buckets"][0]["key"]
    stats["most_active"] = most_active
    attacker_outcome = {}
    for outcome in resource_data["attacker_outcome"]["buckets"]:
        attacker_outcome[outcome["key"]] = outcome["doc_count"]
    stats["attacker_outcome"] = attacker_outcome
    battle_type=[]
    for outcome in resource_data["battle_type"]["buckets"]:
        if outcome["key"]:
            battle_type.append(outcome["key"])
    stats["battle_type"] = battle_type
    defender_size={}
    if resource_data["defender_size"].has_key("avg"):
        defender_size["avg"] = int(resource_data["defender_size"]["avg"])
    if resource_data["defender_size"].has_key("max"):
        defender_size["max"] = int(resource_data["defender_size"]["max"])
    if resource_data["defender_size"].has_key("min"):
        defender_size["min"] = int(resource_data["defender_size"]["min"])
    stats["defender_size"] = defender_size
    event.response = stats



