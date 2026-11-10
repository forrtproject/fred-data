# Build x2_conversion_flags.csv: classifies every chi-squared effect in FReD
# for conversion to r (forrtproject/fred-data#66).
#
# Rule: only chi2(1) from a contingency table, with N = the units in that table,
# is convertible. df > 1 and chi2 / N > 1 are classified automatically; every
# remaining chi2(1) was checked by hand against es_repr and, where needed, the
# source paper (statistics-audit source texts, Nov 2026).
#
# Run from the project root: Rscript pipelines/fred/overlays/build_x2_flags.R
# Reads output/FReD.xlsx only to enumerate the effects; never writes it.

suppressPackageStartupMessages({
  library(dplyr)
  library(stringr)
  library(tibble)
})

reasons <- c(
  contingency = NA_character_,
  df_gt_1 = "chi-squared with df > 1: not a 2 x 2 contingency table",
  ratio_gt_1 = "chi-squared / N > 1: cannot come from a 2 x 2 contingency table with N units",
  model = "chi-squared(1) from a model test (Wald, likelihood-ratio, GEE/GLMM, regression, SEM fit or meta-analytic moderator), not a contingency table",
  goodness_of_fit = "chi-squared(1) goodness-of-fit test against a fixed proportion, not a contingency table",
  n_not_table_units = "contingency-table chi-squared, but the N recorded is not the number of units in the table",
  no_n = "chi-squared without N",
  not_established = "contingency table not established from the source"
)

# Manual decisions for chi2(1) effects. value = es_value regex (NA = all values
# of that fred_id and side). Evidence gives the deciding source passage.
manual <- tribble(
  ~fred_id, ~side, ~value, ~category, ~basis, ~evidence,
  "CORE_160", "o", NA, "goodness_of_fit", "es_repr", "es_repr formula: one-sample chi2 vs 50% split",
  "additional_studies17", "o", NA, "model", "source", "Pigott et al.: moderator tests of the Mantel-Haenszel odds ratio",
  "additional_studies17", "r", NA, "model", "source", "Talbott et al.: moderator tests of the outcome-reporting odds ratio",
  "additional_studies49", "o", NA, "n_not_table_units", "source", "Lozano & Diaz-Negrillo: 2 x 2 chi2 on morpheme frequencies; N = 40 learners, not table counts",
  "additional_studies49", "r", NA, "n_not_table_units", "source", "Kontkanen: suppliance in obligatory contexts; N = 40 learners, not table counts",
  "additional_studies95", "o", NA, "contingency", "source", "Karatas & Cutright Study 2a: binary choice by condition, Phi = 0.15",
  "additional_studies96", "o", NA, "contingency", "source", "Karatas & Cutright Study 2b: binary choice by condition, Phi = 0.14",
  "additional_studies99", "o", NA, "contingency", "source", "Karatas & Cutright Study 3: AI preference 33.5% vs 44.3% by condition, Phi = 0.11",
  "XPHI1", "o", NA, "contingency", "source", "Knobe 2003: intentional yes/no, harm vs help",
  "XPHI11", "o", NA, "contingency", "source", "Knobe & Burra 2006: yes/no judgements compared between conditions",
  "XPHI11", "r", NA, "contingency", "source", "Cova et al. replication of Knobe & Burra harm vs help",
  "Boyce_etal2023168", "o", NA, "contingency", "source", "Boyce et al. table: prop 22/60 vs 15/67 (N = 127)",
  "Boyce_etal2023168", "r", NA, "contingency", "source", "Boyce et al. table: prop 11/19 vs 9/17 (N = 36)",
  "Boyce_etal202339", "o", NA, "goodness_of_fit", "source", "Fischer et al. Study 4: 69% vs 31% within the 2-information condition, chi2(1, N = 26)",
  "Boyce_etal202339", "r", NA, "n_not_table_units", "es_repr", "es_repr table 29/9/33/5 sums to 76, N recorded 215",
  "Boyce_etal202347", "o", NA, "contingency", "es_repr", "es_repr: chisq.test on 2 x 2 table 45/28/28/42 (N = 143)",
  "Boyce_etal202329", "r", NA, "contingency", "source", "Boyce et al. table: prop 5/15 vs 2/11 (N = 26)",
  "Boyce_etal202382", "r", NA, "contingency", "es_repr", "es_repr: chisq.test on 2 x 2 table 19/7/14/11 (N = 51)",
  "Camereretal2018_4_1", "o", NA, "model", "source", "Derex et al. 2013: logistic regression on group size",
  "curatescience283_1", "o", NA, "contingency", "es_repr", "es_repr: 2 x 2 framing x choice from reported percentages",
  "curatescience283_1", "r", NA, "contingency", "source", "Many Labs 2 gain vs loss framing x choice",
  "curatescience241_1", "r", NA, "contingency", "source", "Many Labs 1 low vs high category scale x response category",
  "curatescience45", "o", NA, "contingency", "source", "Zhong & Liljenquist Study 4: 74% vs 41% offered help by condition",
  "curatescience46_2", "o", NA, "contingency", "source", "Zhong & Liljenquist Study 4: 74% vs 41% offered help by condition",
  "curatescience47", "o", NA, "contingency", "source", "Zhong & Liljenquist Study 4: 74% vs 41% offered help by condition",
  "curatescience46", "o", NA, "contingency", "source", "Zhong & Liljenquist Study 3: wipe vs pencil choice by recall condition",
  "curatescience50", "o", NA, "contingency", "source", "Carney et al.: 86% vs 60% took the gamble by pose, Phi = .30",
  "Holzmeisteretal2024_26", "o", NA, "no_n", "source", "Ames & Fiske: blame-task selection by condition, chi2(1) = 6.7 printed without N",
  "Holzmeisteretal2024_6", "o", NA, "model", "source", "Morris et al.: mixed-effects likelihood-ratio test (corrected to 21.7)",
  "Holzmeisteretal2024_9", "o", NA, "contingency", "source", "Kouchaki & Gino Study 7b: cheating by condition, Cramer's V = 0.20",
  "OpenMKT4", "o", NA, "contingency", "source", "Romero & Biswas Study 1b: preference 41.3% vs 19.1% by display",
  "osc2015165", "o", NA, "contingency", "source", "Dai et al.: estimation error by endowment condition, odds ratio 3.28",
  "osc2015165", "r", NA, "contingency", "source", "OSC replication of Dai et al., same design",
  "osc201573", "o", NA, "goodness_of_fit", "source", "Morrison & Miller Study 3: sticker ratio vs registered-voter ratio",
  "osc201584", "o", NA, "contingency", "source", "Fischer et al. Study 4 no-focus: Information Quantity x Information Selection",
  "osc201584", "r", NA, "contingency", "source", "OSC replication: Information Quantity x Information Selection, no-focus condition",
  "osc201589", "r", NA, "model", "source", "OSC replication: gender moderation test in Table 3",
  "XPHI12", "o", NA, "goodness_of_fit", "source", "Nichols 2006: 'goodness-of-fit (1, N = 8) = 4.500'",
  "XPHI2", "o", NA, "contingency", "source", "Knobe 2003: intentional yes/no, immoral vs achievement",
  "XPHI2", "r", NA, "contingency", "source", "Cova et al. replication of Knobe 2003, w = 0.60",
  "XPHI32", "o", NA, "model", "source", "Nagel et al. 2013: GEE contrasts",
  "XPHI32", "r", NA, "model", "source", "Cova et al. replication: GEE contrasts",
  "XPHI34", "o", NA, "model", "source", "Rose & Nichols 2013: SEM chi-squared fit test",
  "XPHI34", "r", NA, "model", "source", "Cova et al. replication: SEM chi-squared fit test",
  "XPHI38", "r", NA, "contingency", "source", "Bjornsson et al. replication: yes/no proportions by condition",
  "XPHI7", "o", NA, "goodness_of_fit", "source", "Nahmias et al. 2005: 16:5 goodness-of-fit test",
  "XPHI19", "o", NA, "contingency", "source", "Nadelhoffer & Feltz: permissibility yes/no, actor vs observer (N = 85)",
  "XPHI13", "o", NA, "contingency", "source", "Nadelhoffer 2006: between-condition yes/no (N = 126)",
  "XPHI13", "r", NA, "contingency", "source", "Cova et al. replication: between-condition yes/no (N = 259)",
  "CORE_50", "o", NA, "goodness_of_fit", "es_repr", "es_repr: chisq.test(c(17, 121), p = c(0.5, 0.5))",
  "CORE_50", "r", NA, "goodness_of_fit", "es_repr", "Kutscher & Feldman: 315 vs 27 choosing one option",
  "CORE_70", "o", NA, "goodness_of_fit", "source", "Pronin et al. 2002, note 7: tested against an assumed 46 of 91",
  "CORE_70", "r", NA, "goodness_of_fit", "source", "Chandrashekar et al.: 'comparing to a 50%-50% split'",
  "CORE_102", "o", "12\\.6", "goodness_of_fit", "es_repr", "es_repr: chisq.test(c(20, 3), p = c(0.5, 0.5))",
  "CORE_102", "o", "4\\.54", "contingency", "source", "Connolly et al.: 20/23 vs 24/39 between conditions (N = 62)",
  "CORE_86", "o", NA, "goodness_of_fit", "source", "Spranca et al. Exp 1: within-subject counts (37 of 57); no contingency table",
  "add_ai5", "o", "= 0\\.0$", "n_not_table_units", "source", "Cialdini et al. Exp 3: contrast of the two control conditions (48 of 72 subjects)",
  "add_ai5", "o", "2\\.88", "contingency", "source", "Cialdini et al. Exp 3: rejection-moderation vs combined controls (N = 72)",
  "add_ai5", "r", "2\\.11", "n_not_table_units", "source", "Genschow et al.: contrast of the two control conditions, a subset of N = 391",
  "add_ai5", "r", "10\\.82", "contingency", "source", "Genschow et al.: rejection-moderation vs combined controls (N = 391)",
  "additional_studies223", "o", NA, "model", "source", "Bryan et al. 2011: likelihood-ratio test from logistic regression",
  "add_ai73", "o", "5\\.5", "n_not_table_units", "source", "Sanders et al. 1993 Table 1: allele counts (2N), N recorded 106 people",
  "add_ai73", "o", "6\\.67", "df_gt_1", "source", "Sanders et al. 1993 Table 2: 2 x 3 genotype table (df = 2)",
  "add_ai73", "r", "0\\.036", "n_not_table_units", "source", "Nothen et al. 1993 Table I: allele frequencies (2N), N recorded 167 people",
  "add_ai73", "r", "3\\.481", "df_gt_1", "source", "Nothen et al. 1993 Table II: 2 x 3 genotype table, p = .175 implies df = 2",
  "FORRT_781a", "o", NA, "goodness_of_fit", "es_repr", "es_repr: one-sample chi2 on 12 of 16 choices",
  "FORRT_781b", "o", NA, "goodness_of_fit", "es_repr", "es_repr: one-sample chi2 on 12 of 16 choices",
  "FORRT_781a", "r", NA, "goodness_of_fit", "es_repr", "es_repr: one-sample chi2 on 18 of 32 choices",
  "FORRT_781b", "r", NA, "goodness_of_fit", "es_repr", "es_repr: one-sample chi2 on 15 of 24 choices",
  "soscisubmission34", "r", NA, "contingency", "source", "Ross & Levy H1: Republicans (422) vs Democrats (532) = 954",
  "soscisubmission34_2_1", "r", NA, "n_not_table_units", "source", "Ross & Levy H14: among 303 Trump voters, N recorded 954",
  "soscisubmission34_2_2", "r", NA, "n_not_table_units", "source", "Ross & Levy H8: Trump (303) vs Clinton (333) voters, N recorded 954",
  "additional_studies235", "r", NA, "model", "source", "Ebert et al. 2024: GLMM chi-squared tests (Tables 1-9)",
  "av_36", "r", NA, "goodness_of_fit", "source", "Collier & Lawson: 'chi-square test of goodness-of-fit'"
)

fred <- openxlsx::read.xlsx("output/FReD.xlsx")
sides <- lapply(c("o", "r"), function(s) {
  tibble(fred_id = fred$fred_id, side = s,
         es_type = fred[[paste0("es_type_", s)]], es_value = fred[[paste0("es_value_", s)]],
         es_repr = fred[[paste0("es_repr_", s)]])
})
x2 <- bind_rows(sides) %>%
  filter(str_detect(es_value, regex("^\\s*(X2|χ2|χ²)", ignore_case = TRUE))) %>%
  distinct(fred_id, side, es_value, .keep_all = TRUE)

m <- str_match(x2$es_value, "^X2\\((\\d+(?:\\.\\d+)?)(?:, (?:N = )?(\\d+(?:\\.\\d+)?))?\\) = (\\d*\\.?\\d+)$")
x2 <- x2 %>% mutate(df = as.numeric(m[, 2]), n_x2 = as.numeric(m[, 3]), chi2 = as.numeric(m[, 4]))
stopifnot(!anyNA(x2$df))

lookup <- function(id, sd, val) {
  hit <- manual %>% filter(fred_id == id, side == sd, is.na(value) | str_detect(val, coalesce(value, ".")))
  if (nrow(hit) > 1) stop("Ambiguous manual decision: ", id, " ", sd, " ", val)
  hit
}

auto_ratio <- !is.na(x2$n_x2) & x2$chi2 / x2$n_x2 > 1
x2$category <- ifelse(x2$df > 1, "df_gt_1", ifelse(auto_ratio, "ratio_gt_1", NA))
x2$basis <- ifelse(is.na(x2$category), NA, "automatic")
x2$evidence <- NA_character_
for (i in which(is.na(x2$category))) {
  hit <- lookup(x2$fred_id[i], x2$side[i], x2$es_value[i])
  if (nrow(hit) == 1) {
    x2$category[i] <- hit$category
    x2$basis[i] <- hit$basis
    x2$evidence[i] <- hit$evidence
  }
}
flags <- x2

unclassified <- flags %>% filter(is.na(category))
if (nrow(unclassified) > 0) {
  print(unclassified)
  stop("Unclassified chi-squared effects; add manual decisions.")
}
unused <- anti_join(manual, flags, by = c("fred_id", "side"))
if (nrow(unused) > 0) stop("Manual decisions without a matching effect: ", paste(unused$fred_id, collapse = ", "))

flags <- flags %>%
  mutate(convertible = category == "contingency",
         reason = unname(reasons[category])) %>%
  select(fred_id, side, es_value, es_type, df, n_x2, chi2, convertible, category, reason, basis, evidence) %>%
  arrange(side, fred_id, es_value)

write.csv(flags, "pipelines/fred/overlays/x2_conversion_flags.csv", row.names = FALSE, na = "")
print(count(flags, convertible, basis))
print(count(flags, category))
