.sep ,
.output multiplicity.csv
select lower(claim_name) as name, count(*) as num_claims from claim where claim_type = 2 group by name having num_claims >= 5 order by num_claims desc;
