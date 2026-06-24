"""Find complete-genome NCBI accessions for SARS-CoV-2 lineages."""

import json
import time
import urllib.parse
import urllib.request

SEARCHES = {
    "BA.2.75.2": '"Severe acute respiratory syndrome coronavirus 2"[Organism] AND BA.2.75.2[All Fields] AND 29000:31000[SLEN]',
    "BQ.1.1": '"Severe acute respiratory syndrome coronavirus 2"[Organism] AND BQ.1.1[All Fields] AND 29000:31000[SLEN]',
    "XBB.1.5": '"Severe acute respiratory syndrome coronavirus 2"[Organism] AND XBB.1.5[All Fields] AND 29000:31000[SLEN]',
}


def esearch(term):
    params = urllib.parse.urlencode({"db": "nuccore", "term": term, "retmax": 5, "retmode": "json"})
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?{params}"
    with urllib.request.urlopen(url, timeout=30) as resp:
        data = json.loads(resp.read().decode())
    return data["esearchresult"].get("idlist", [])


def esummary(ids):
    params = urllib.parse.urlencode({"db": "nuccore", "id": ",".join(ids), "retmode": "json"})
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?{params}"
    with urllib.request.urlopen(url, timeout=30) as resp:
        return json.loads(resp.read().decode())["result"]


def main():
    for lineage, term in SEARCHES.items():
        print(f"=== {lineage} ===")
        ids = esearch(term)
        if not ids:
            print("no hits")
            continue
        summary = esummary(ids)
        for uid in summary.get("uids", []):
            item = summary[uid]
            print(item.get("accessionversion"), item.get("slen"), item.get("title", "")[:110])
        time.sleep(0.4)


if __name__ == "__main__":
    main()
