# clean_data.R
# Normalize raw NASS data and output clean .rds files for the dashboard.
#
# Two inputs:
#   nass_raw.rds       — county-level data (area, yield, value where available)
#   nass_state_raw.rds — CA statewide price received + value of production
#
# NASS county-level stat categories:
#   Area:  "AREA HARVESTED", "AREA BEARING & NON-BEARING"
#   Yield: "YIELD"
#   Value: "SALES" (Cotton/Milk/Tomatoes only — others not published at county)
# NASS state-level stat categories:
#   "PRICE RECEIVED", "VALUE"

library(tidyverse)

PROJ_ROOT <- path.expand("~/Documents/GitHub/Portfolio/R_Projects/Central_Valley_Ag_Economics")

raw_county <- readRDS(file.path(PROJ_ROOT, "data/raw/nass_raw.rds"))
raw_state  <- readRDS(file.path(PROJ_ROOT, "data/raw/nass_state_raw.rds"))

# ---- shared cleaning function -------------------------------------
clean_raw <- function(df, geo) {
  df |>
    filter(domain_desc == "TOTAL") |>
    select(year, county_name, commodity_desc, statisticcat_desc, unit_desc, Value) |>
    rename(
      county    = county_name,
      crop      = commodity_desc,
      metric    = statisticcat_desc,
      unit      = unit_desc,
      value_raw = Value
    ) |>
    mutate(
      geo_level = geo,
      year      = as.integer(year),
      county    = str_to_title(county),
      county    = if_else(geo_level == "state", "CA Statewide", county),
      crop      = str_to_title(crop),

      value = case_when(
        str_trim(value_raw) %in% c("(D)", "(Z)", "(L)", "(H)", "(NA)") ~ NA_real_,
        TRUE ~ suppressWarnings(as.numeric(str_remove_all(value_raw, ",")))
      ),

      unit_std = case_when(
        str_detect(unit, "\\$")    ~ "usd",   # must be first — "$ / CWT", "$ / LB" etc.
        str_detect(unit, "TONS")   ~ "tons",
        str_detect(unit, "CWT")    ~ "cwt",
        str_detect(unit, "LB")     ~ "lbs",
        str_detect(unit, "ACRE")   ~ "acres",
        str_detect(unit, "HEAD")   ~ "head",
        TRUE                       ~ str_to_lower(unit)
      ),

      crop_label = case_when(
        str_detect(crop, "Tomato") ~ "Tomatoes",
        TRUE                       ~ word(crop, 1)
      ),

      metric_label = case_when(
        metric %in% c("AREA HARVESTED",
                      "AREA IN PRODUCTION",
                      "AREA BEARING",
                      "AREA BEARING & NON-BEARING") ~ "Acres Harvested",
        metric == "YIELD"                                         ~ "Yield per Acre",
        metric == "PRICE RECEIVED"                                ~ "Price Received",
        # PRODUCTION in $ = value of production (state level for all crops)
        # SALES in $ = value of production (county level for Cotton/Milk/Tomatoes)
        # GROSS INCOME in $ = Milk value alternative
        metric %in% c("PRODUCTION", "SALES", "GROSS INCOME",
                      "VALUE", "RECEIPTS")                        ~ "Value of Production",
        TRUE                                                      ~ str_to_title(metric)
      ),

      area_priority = case_when(
        metric == "AREA HARVESTED"             ~ 1L,
        metric == "AREA BEARING & NON-BEARING" ~ 2L,
        metric == "AREA BEARING"               ~ 3L,
        TRUE                                   ~ 4L
      )
    ) |>
    filter(
      metric_label %in% c("Acres Harvested", "Yield per Acre",
                          "Price Received", "Value of Production"),
      !is.na(value),
      !(metric_label == "Acres Harvested"     & unit_std != "acres"),
      !(metric_label == "Value of Production" & unit_std != "usd"),
      !(metric_label == "Price Received"      & unit_std != "usd")
    ) |>
    group_by(geo_level, year, county, crop_label, metric_label) |>
    slice_min(area_priority, n = 1, with_ties = FALSE) |>
    ungroup() |>
    select(geo_level, year, county, crop, crop_label,
           metric, metric_label, unit, unit_std, value)
}

county_clean <- clean_raw(raw_county, "county")
state_clean  <- clean_raw(raw_state,  "state")

# Combined: county rows first; state fills in crops/metrics absent at county level.
# For the trend + price charts we use the full combined set.
# For county comparison charts the dashboard filters to geo_level == "county".
clean <- bind_rows(county_clean, state_clean)

# ---- Derived: value per acre (county level only) ------------------
area <- county_clean |>
  filter(metric_label == "Acres Harvested") |>
  select(year, county, crop_label, acres = value)

value_prod <- county_clean |>
  filter(metric_label == "Value of Production") |>
  select(year, county, crop_label, value_prod = value)

derived <- area |>
  inner_join(value_prod, by = c("year", "county", "crop_label")) |>
  mutate(value_per_acre = value_prod / acres) |>
  filter(is.finite(value_per_acre))

# ---- Yield index (county level only) ------------------------------
yield_data <- county_clean |>
  filter(metric_label == "Yield per Acre") |>
  group_by(crop_label, county) |>
  mutate(
    base        = mean(value[year == 2015], na.rm = TRUE),
    yield_index = if_else(!is.na(base) & base > 0, value / base * 100, NA_real_)
  ) |>
  ungroup() |>
  select(-base)

saveRDS(clean,      file.path(PROJ_ROOT, "data/cv_ag_clean.rds"))
saveRDS(derived,    file.path(PROJ_ROOT, "data/cv_ag_derived.rds"))
saveRDS(yield_data, file.path(PROJ_ROOT, "data/cv_ag_yield_index.rds"))

message("=== Clean data summary ===")
clean |> count(geo_level, crop_label, metric_label) |>
  arrange(geo_level, crop_label, metric_label) |>
  with(message(paste(
    sprintf("  [%-6s] %-12s | %-22s | %d rows", geo_level, crop_label, metric_label, n),
    collapse = "\n"
  )))
message(sprintf("\nDerived (value/acre, county): %d rows", nrow(derived)))
message(sprintf("Yield index (county):         %d rows", nrow(yield_data)))
