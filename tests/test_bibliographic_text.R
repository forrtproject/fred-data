# Rscript tests/test_bibliographic_text.R
source(here::here("R", "data_cleaning.R"))

stopifnot(
  identical(decode_html_entities(c("Fath &amp; Kay", "&#233;t&#xE9;", "a &amp;lt; b", NA)),
            c("Fath & Kay", "été", "a &lt; b", NA)),
  identical(strip_markup_tags("the <scp>expectancy</scp> theory, <i>OSF</i><sup>**</sup>"),
            "the expectancy theory, OSF**"),
  identical(strip_markup_tags("p <.05 and r> .3"), "p <.05 and r> .3"),
  identical(escape_bibtex_ampersands("title={Fath & Kay}, url={https://x.org/?a=1&b=2}, journal={A \\& B}"),
            "title={Fath \\& Kay}, url={https://x.org/?a=1&b=2}, journal={A \\& B}")
)

df <- data.frame(ref_r = "Fath &amp; Kay. <i>OSF</i>", bibtex_r = "title={Fath &amp; Kay}",
                 description = "p <.05 &amp; more", n_r = 10)
out <- clean_bibliographic_text(df)
stopifnot(identical(out$ref_r, "Fath & Kay. OSF"), identical(out$bibtex_r, "title={Fath \\& Kay}"),
          identical(out$description, "p <.05 & more"), identical(out$n_r, 10))
cat("bibliographic text tests passed\n")
