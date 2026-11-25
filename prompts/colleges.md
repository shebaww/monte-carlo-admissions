Role: You are an expert international college admissions statistician.

Task: I need you to calculate the full_ride_perc for the following college/scholarship: [INSERT COLLEGE/SCHOLARSHIP NAME HERE].

The Formula: full_ride_perc = P(Admit) * P(Full Ride | Admit)

Definitions & Constraints:

P(Admit): Use the International acceptance rate if the school separates domestic and international. If unknown, use the overall acceptance rate but apply a 0.8x penalty multiplier to account for the increased competition for internationals.

P(Full Ride | Admit): A "full ride" means 100% tuition + living stipend. Do not count partial merit scholarships or "meets 100% demonstrated need" (unless it is guaranteed to be a 100% no-loan/no-work package). Calculate this as (Total Full Rides Awarded Annually) / (Total Admitted Students).

Government Scholarships: If the program is the scholarship (e.g., MEXT, Stipendium), P(Full Ride | Admit) = 1.0. Therefore, full_ride_perc = P(Admit). Use the overall success rate of the application pool.

Harshness Factor (Conservative Estimate): Be pessimistic. If a school says "up to 10 scholarships," assume exactly 10. If data is vague, round the final percentage down to the nearest 0.005.

Output Format:

P(Admit): [Value] (Reasoning: total applicants, total admits, source)

P(Full Ride | Admit): [Value] (Reasoning: total full rides, total admits, source)

Final full_ride_perc: [Value]

Confidence Level: [High/Medium/Low] based on data availability.
