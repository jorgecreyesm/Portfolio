# fetch_data.R
# Pull Central Valley crop data from USDA NASS Quick Stats API.
# Results are cached as .rds in data/raw/ — run once before knitting.
#
# Two fetch passes:
#   1. County level  — all metrics per crop/county (no statisticcat_desc filter
#      because rnassqs returns 0 rows when statisticcat_desc + county_name are
#      combined in the same query).
#   2. State level   — Price Received + Value of Production only; these are not
#      published at county level in NASS Quick Stats but are needed for the
#      statewide trend and price charts.

library(rnassqs)
library(tidyverse)

PROJ_ROOT <- path.expand("~/Documents/GitHub/Portfolio/R_Projects/Central_Valley_Ag_Economics")
api_key   <- trimws(readLines(file.path(PROJ_ROOT, ".env"))[1])
api_key   <- sub("NASS_API_KEY=", "", api_key)
nassqs_auth(key = api_key)

message("Testing API connection...")
test <- tryCatch(
  nassqs(list(
    commodity_desc = "ALMONDS",
    state_alpha    = "CA",
    agg_level_desc = "STATE",
    year__GE       = 2020,
    year__LE       = 2022
  )),
  error = function(e) { message("Connection failed: ", e$message); NULL }
)
if (is.null(test) || nrow(test) == 0) stop("API test returned no data. Check key and connection.")
message(sprintf("Connection OK — test returned %d rows.", nrow(test)))

# ------------------------------------------------------------------
COUNTIES <- c("FRESNO", "TULARE", "KINGS", "MERCED",
               "SAN JOAQUIN", "STANISLAUS", "MADERA")

COMMODITIES <- c(
  "GRAPES",
  "ALMONDS",
  "TOMATOES",
  "WALNUTS",
  "MILK",
  "COTTON"
)

# --- Pass 1: County level -------------------------------------------
fetch_county <- function(commodity, county) {
  Sys.sleep(0.4)
  tryCatch({
    result <- nassqs(list(
      commodity_desc = commodity,
      state_alpha    = "CA",
      county_name    = county,
      agg_level_desc = "COUNTY",
      year__GE       = 2010,
      year__LE       = 2024
    ))
    if (nrow(result) > 0) {
      message(sprintf("  + %4d rows: %-25s | %s", nrow(result), commodity, county))
      result
    } else {
      message(sprintf("  0 rows:   %-25s | %s", commodity, county))
      NULL
    }
  }, error = function(e) {
    message(sprintf("  ERROR:    %-25s | %-15s | %s", commodity, county, e$message))
    NULL
  })
}

all_county <- list()
for (commodity in COMMODITIES) {
  message(sprintf("\n[County] Fetching: %s", commodity))
  for (county in COUNTIES) {
    result <- fetch_county(commodity, county)
    if (!is.null(result)) all_county[[length(all_county) + 1]] <- result
  }
}

county_df <- bind_rows(all_county)
message(sprintf("\nCounty fetch done: %d rows", nrow(county_df)))

# --- Pass 2: State level (all metrics — no statisticcat_desc filter) --------
# statisticcat_desc causes HTTP 400 on some state-level queries, same as county.
# Fetch everything per commodity and let clean_data.R filter what's needed.
fetch_state <- function(commodity) {
  Sys.sleep(0.4)
  tryCatch({
    result <- nassqs(list(
      commodity_desc = commodity,
      state_alpha    = "CA",
      agg_level_desc = "STATE",
      year__GE       = 2010,
      year__LE       = 2024
    ))
    if (nrow(result) > 0) {
      message(sprintf("  + %4d rows: %s", nrow(result), commodity))
      result
    } else {
      message(sprintf("  0 rows:   %s", commodity))
      NULL
    }
  }, error = function(e) {
    message(sprintf("  ERROR:    %-25s | %s", commodity, e$message))
    NULL
  })
}

all_state <- list()
message("\n[State] Fetching all metrics per commodity...")
for (commodity in COMMODITIES) {
  result <- fetch_state(commodity)
  if (!is.null(result)) all_state[[length(all_state) + 1]] <- result
}

state_df <- bind_rows(all_state)
message(sprintf("\nState fetch done: %d rows", nrow(state_df)))

# --- Save both to raw/ ----------------------------------------------
saveRDS(county_df, file.path(PROJ_ROOT, "data/raw/nass_raw.rds"))
saveRDS(state_df,  file.path(PROJ_ROOT, "data/raw/nass_state_raw.rds"))
message(sprintf("\nSaved %d county rows → data/raw/nass_raw.rds", nrow(county_df)))
message(sprintf("Saved %d state rows  → data/raw/nass_state_raw.rds", nrow(state_df)))

# Summary
message("\nState-level statisticcat_desc by commodity:")
if (nrow(state_df) > 0) {
  state_df |>
    count(commodity_desc, statisticcat_desc) |>
    arrange(commodity_desc, statisticcat_desc) |>
    with(message(paste(sprintf("  %-25s | %s (n=%d)", commodity_desc, statisticcat_desc, n),
                       collapse = "\n")))
}
