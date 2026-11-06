SELECT g.product_line,
       SUM(p.premium_amt_gross) - SUM(p.cancellation_amt) AS net_written_premium
FROM analytics.fct_premiums x
JOIN analytics.fct_policy_premium p ON x.pol_id = p.policy_id
JOIN analytics.dim_geography g ON p.agent_id = g.geo_id
GROUP BY g.product_line, p.eff_dt
