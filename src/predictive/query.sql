with step1 as (
select uf, ra, óbito, strftime('%Y-%m-%d', 
    substr(dataprimeirosintomas, 7, 4) || '-' || 
    substr(dataprimeirosintomas, 4, 2) || '-' || 
    substr(dataprimeirosintomas, 1, 2)) as data
from historical_data 
where dataprimeirosintomas <> '' or dataprimeirosintomas is not null
),

step2 as (
select data, ra, count(*) as case_cnt, 
    sum(case when lower(trim(óbito)) != 'não' then 1 else 0 end) as death_cnt
from step1
group by data, ra
)

select 
'brasilia' as country, lower(s2.ra) as province, s2.data as date,
s2.case_cnt, s2.death_cnt
from step2 s2
where s2.ra is not null and trim(ra) <> 'Não Informado' and trim(ra) <> ''
order by s2.data
