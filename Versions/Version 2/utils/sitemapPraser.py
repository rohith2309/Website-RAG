import xml.etree.ElementTree as ET
import requests
import logging

logging.basicConfig(level=logging.INFO)

def get_sitemap_urls(url:str)->list[str]:
    
    namespace = {
        "sm": "http://www.sitemaps.org/schemas/sitemap/0.9"
    }
    
    urls = []
    
    try:
        sitemap_url = url+"/sitemap.xml"
        sitemap_index_url = url+"/sitemap_index.xml"
     

        #try to get sitemap_url.xml first
        response = requests.get(sitemap_url)
        if response.status_code == 200 :
            root = ET.fromstring(response.content)
        
            for url in root.findall("sm:url",namespace):
                loc = url.find("sm:loc",namespace)
                if loc is not None:
                  urls.append(loc.text)
        else:
            response = requests.get(sitemap_index_url)
            if response.status_code != 200 :
                print(f"Failed to fetch sitemap_index.xml: {response.status_code}")
                raise Exception(f"Failed to fetch sitemap_index.xml and sitemao: {response.status_code}")
            root = ET.fromstring(response.content)
            for url in root.findall("sm:url",namespace):
                loc = url.find("sm:loc",namespace)
                if loc is not None:
                    urls.append(loc.text)
    except Exception as e:
        print(f"Error fetching or parsing sitemap: {e}")
                        
    logging.info(f"Found {len(urls)} URLs in the sitemap.")
    return urls                
                      
                     
            