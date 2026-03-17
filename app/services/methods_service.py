from fastapi import HTTPException
from pathlib import Path
import logging
import httpx
from app.config.settings import settings
from app.repositories.methods_repository import get_methods_from_db
from app.repositories.task_repository import update_task
from app.util.bypass_security_controls import execute_ssl_pinning_bypass, mimic_human_behavior_delays

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

logger = logging.getLogger(__name__)

def get_methods_with_url(app: str, methods_db_path: Path) -> dict[str: str]:
    methods_db_data = get_methods_from_db(methods_db_path)

    matched_app = next((app_name for app_name in methods_db_data if app_name.lower() == app.lower()), None)
    if matched_app is None:
        raise HTTPException(status_code=404, detail="App not yet available for reverse engineering")
    return methods_db_data.get(matched_app, {}).get("methods", {})

def get_method_names(app:str, methods_db_path: Path) -> list[str]:
    methods_with_url = get_methods_with_url(app, methods_db_path)
    return list(methods_with_url.keys())

# As the methods grow, we can create separate services file for each app.

async def execute_olx_search(task_id: str, search_term: str):
    try:
        url = get_methods_with_url("OLX", settings.get_methods_db_path()).get("search_ads")
        if not url:
            raise ValueError("Method 'search_ads' not found for OLX")
        
        update_task(task_id, "processing", message="Mimicking human behavious before sending request")
        logger.info("task_id=%s status=%s message=%s", task_id, "processing", "Mimicking human behavior before sending request")

        await mimic_human_behavior_delays()

        update_task(task_id, "processing", message="Sending request to OLX API")
        logger.info("task_id=%s status=%s message=%s", task_id, "processing", "Sending request to OLX API")

        headers = {
            "X-Apollo-Operation-Id": "2f81b5cd3eb6da0e44a0588fafbc420a0fc706ef853672180e8ffaf7182681f0",
            "X-Apollo-Operation-Name": "AdListingsQuery",
            "Accept": "multipart/mixed; deferSpec=20220824, application/json",
            "X-Sitecode": "olxpt",
            "Accept-Language": "pt",
            "Version": "v1.21",
            "X-Device-Id": "73B18A39C41954F073DD785FE6D60235GompDgvlBJF5NoVi7A",
            "X-Platform-Type": "android",
            "User-Agent": "Android App Ver 5.154.5 (Android 9.0;)",
            "Laquesis": "rnk-2687@a#ream-1925@a#rnk-2821@c#ema-458@b#recpl-1308@b",
            "Content-Type": "application/json"
        }

        payload = {
            "operationName": "AdListingsQuery",
            "variables": {
                "searchParameters": [
                    {"key": "query", "value": search_term},
                    {"key": "sort_by", "value": "relevance:desc"},
                    {"key": "sl", "value": "19ceeff061exddf02080"}
                ],
                "withPayAndShip": False,
                "withVerificationStatus": True
            },
            "query": "query AdListingsQuery($searchParameters: [SearchParameter!], $withPayAndShip: Boolean!, $withVerificationStatus: Boolean!) { clientCompatibleListings(searchParameters: $searchParameters) { __typename ... on ListingSuccess { __typename metadata { total_elements visible_total_count search_suggestion { changes { query category_id city_id distance district_id region_id } type url } sub_sections { ads_idx message } facets { category { count id label url } city { count id label url } district { count id label url } region { count id label url } } new promoted source search_id filter_suggestions { category constraints { type } label name type unit values { label value } } adverts { config { targeting } } } links { first { href } next { href } previous { href } self { href } } data { __typename ...GraphQlAd } } } }  fragment GraphQlAd on LegacyAdvert { params { key name type value { __typename ... on GenericParam { key label } ... on CheckboxesParam { label checkboxeskey: key } ... on PriceParam { value type arranged budget converted_currency converted_previous_value converted_value currency label negotiable previous_label previous_value } ... on SalaryParam { from to arranged converted_currency converted_from converted_to currency gross type } ... on ErrorParam { message } } } category { id type } contact { chat courier name negotiation phone } delivery { rock { active mode offer_id } } external_url id last_refresh_time location { city { id name normalized_name } district { name normalized_name id } region { id name normalized_name } } omnibus_pushup_time promotion { b2c_ad_page highlighted options premium_ad_page top_ad urgent } safedeal { allowed_quantity weight_grams } shop { subdomain } title url user { about banner_desktop company_name created id is_online last_seen logo logo_ad_page name other_ads_enabled photo seller_type social_network_account_type uuid banner_mobile b2c_business_page verification @include(if: $withVerificationStatus) { status } } business photos { link width height filename id rotation } valid_to_time created_time description key_params offer_type map { lat lon radius zoom show_detailed } partner { code } protect_phone status payAndShip @include(if: $withPayAndShip) { sellerPaidDeliveryEnabled } }"
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            update_task(task_id, "completed", result=response.json(), message="Method executed successfully")
            logger.info("task_id=%s status=%s message=%s", task_id, "completed", "Method executed successfully")
            
    except Exception as e:
        update_task(task_id, "failed", message=f"Error executing method: {str(e)}")
        logger.exception("task_id=%s status=%s message=%s", task_id, "failed", f"Error executing method: {str(e)}")

# This is just for testing the direct execution without using the background tasks code flow.
async def execute_olx_search_direct(search_term: str) -> dict:
    url = get_methods_with_url("OLX", settings.get_methods_db_path()).get("search_ads")
    if not url:
        raise ValueError("Method 'search_ads' not found for OLX")
    
    headers = {
        "X-Apollo-Operation-Id": "2f81b5cd3eb6da0e44a0588fafbc420a0fc706ef853672180e8ffaf7182681f0",
        "X-Apollo-Operation-Name": "AdListingsQuery",
        "Accept": "multipart/mixed; deferSpec=20220824, application/json",
        "X-Sitecode": "olxpt",
        "Accept-Language": "pt",
        "Version": "v1.21",
        "X-Device-Id": "73B18A39C41954F073DD785FE6D60235GompDgvlBJF5NoVi7A",
        "X-Platform-Type": "android",
        "User-Agent": "Android App Ver 5.154.5 (Android 9.0;)",
        "Laquesis": "rnk-2687@a#ream-1925@a#rnk-2821@c#ema-458@b#recpl-1308@b",
        "Content-Type": "application/json"
    }

    payload = {
        "operationName": "AdListingsQuery",
        "variables": {
            "searchParameters": [
                {"key": "query", "value": search_term},
                {"key": "sort_by", "value": "relevance:desc"},
                {"key": "sl", "value": "19ceeff061exddf02080"}
            ],
            "withPayAndShip": False,
            "withVerificationStatus": True
        },
        "query": "query AdListingsQuery($searchParameters: [SearchParameter!], $withPayAndShip: Boolean!, $withVerificationStatus: Boolean!) { clientCompatibleListings(searchParameters: $searchParameters) { __typename ... on ListingSuccess { __typename metadata { total_elements visible_total_count search_suggestion { changes { query category_id city_id distance district_id region_id } type url } sub_sections { ads_idx message } facets { category { count id label url } city { count id label url } district { count id label url } region { count id label url } } new promoted source search_id filter_suggestions { category constraints { type } label name type unit values { label value } } adverts { config { targeting } } } links { first { href } next { href } previous { href } self { href } } data { __typename ...GraphQlAd } } } }  fragment GraphQlAd on LegacyAdvert { params { key name type value { __typename ... on GenericParam { key label } ... on CheckboxesParam { label checkboxeskey: key } ... on PriceParam { value type arranged budget converted_currency converted_previous_value converted_value currency label negotiable previous_label previous_value } ... on SalaryParam { from to arranged converted_currency converted_from converted_to currency gross type } ... on ErrorParam { message } } } category { id type } contact { chat courier name negotiation phone } delivery { rock { active mode offer_id } } external_url id last_refresh_time location { city { id name normalized_name } district { name normalized_name id } region { id name normalized_name } } omnibus_pushup_time promotion { b2c_ad_page highlighted options premium_ad_page top_ad urgent } safedeal { allowed_quantity weight_grams } shop { subdomain } title url user { about banner_desktop company_name created id is_online last_seen logo logo_ad_page name other_ads_enabled photo seller_type social_network_account_type uuid banner_mobile b2c_business_page verification @include(if: $withVerificationStatus) { status } } business photos { link width height filename id rotation } valid_to_time created_time description key_params offer_type map { lat lon radius zoom show_detailed } partner { code } protect_phone status payAndShip @include(if: $withPayAndShip) { sellerPaidDeliveryEnabled } }"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()

def execute_method_with_app_access():
    methods_db_data = get_methods_from_db(settings.get_methods_db_path())
    package_name = methods_db_data.get("OLX", {}).get("name")
    result = execute_ssl_pinning_bypass(package_name)
    if result == True:
        return {"message": "SSL pinning bypass executed successfully"}
    else:
        return {"message": "Failed to execute SSL pinning bypass"}
