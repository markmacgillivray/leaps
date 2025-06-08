import csv, json, requests

h = 'http://localhost:9200/leaps_simd/_doc/'

rows = csv.DictReader(open('SIMD_2020_v2_updated_2025.csv','r'))

count = 0
hasnew = 0
for row in rows:
    id = row['Postcode'].lower().replace(' ','')
    r = requests.get(h+id)
    data = {}
    if r.status_code == 200:
        data['2020_v2'] = r.json()['_source']
        data['created_date'] = data['2020_v2']['created_date']
    else:
        data['created_date'] = '2025-06-06 1400'
        hasnew += 1
    data['last_updated'] = '2025-06-06 1400'
    data['id'] = id
    data['post_code'] = row['Postcode']
    data['DZ'] = row['DZ']
    data['simd_rank'] = row['SIMD2020_Rank']
    data['simd_vigintile'] = row['SIMD2020_Vigintile']
    data['simd_decile'] = row['SIMD2020_Decile']
    data['simd_quintile'] = row['SIMD2020_Quintile']
    res = requests.post(h+id,data=json.dumps(data))
    print(res.status_code)
    count += 1
    print(count)

print('done')
print(count)
print(hasnew)
