from pathlib import Path

import pandas as pd
import streamlit as st

DATA = Path(__file__).parent / "results"

st.set_page_config(page_title="Data validation demo", layout="wide")



@st.cache_data
def load():
    results = pd.read_csv(DATA / "results.csv")
    flagged = pd.read_csv(DATA / "flagged_cells.csv", dtype=str).fillna("")
    cols = pd.read_csv(DATA / "column_recall.csv")
    missed = pd.read_csv(DATA / "missed_cells.csv", dtype=str)
    summary = pd.read_csv(DATA / "summary.csv").iloc[0]
    return results, flagged, cols, missed, summary


results, flagged, cols, missed, s = load()
final = results[results["checker"].str.contains("final")].iloc[0]

st.title("Rule-based data validation on the Hospital benchmark")
st.caption(
    "Public benchmark data (Raha/Baran Hospital dataset). Educational demo; "
    "not based on any company's data and not affiliated with any company."
)

st.markdown(
    f"**In plain words:** a table of {int(s.rows):,} hospital records contains {int(s.wrong_cells)} wrong values. "
    f"A small set of explainable rules finds {int(final.true_errors_found)} of them with {int(final.false_alarms)} false alarms, "
    f"and proposes a fix for {int(s.repairs_attempted)} of them ({int(s.repairs_correct)} of those fixes were correct). "
    "The rest are listed under *What is missed*, with the limits of the approach."
)

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Wrong cells", int(s.wrong_cells), help=f"{int(s.rows)} rows x {int(s.data_columns)} data columns")
c2.metric("Flagged by final checker", int(final.flagged))
c3.metric("Recall", f"{final.recall:.1%}")
c4.metric("Precision", f"{final.precision:.1%}")
c5.metric("Repairs correct", f"{int(s.repairs_correct)} / {int(s.repairs_attempted)}")

tab1, tab2, tab3, tab4 = st.tabs(["Checkers compared", "Flagged cells", "What is missed", "About"])

with tab1:
    st.subheader("Precision and recall by checker")
    st.bar_chart(results.set_index("checker")[["precision", "recall"]])
    st.dataframe(results, hide_index=True)
    st.info(
        "The 'contains x' row is a shortcut specific to this benchmark (its errors are mostly "
        "random 'x' characters), not a realistic check. The final checker uses format and "
        "consistency rules that do not rely on that trick."
    )

with tab2:
    st.subheader("Cells flagged by the final checker")
    choice = st.multiselect("Filter by column", sorted(flagged["column"].unique()))
    only_fix = st.checkbox("Only cells with a suggested fix")
    view = flagged[flagged["column"].isin(choice)] if choice else flagged
    if only_fix:
        view = view[view["suggested_value"] != ""]
    st.caption(f"{len(view)} cells shown")
    st.bar_chart(view["column"].value_counts())
    st.dataframe(view, hide_index=True)

with tab3:
    st.subheader("Recall by column")
    st.bar_chart(cols.dropna(subset=["recall"]).set_index("column")["recall"])
    st.dataframe(cols, hide_index=True)
    st.subheader("Errors the final checker missed")
    st.dataframe(missed, hide_index=True)
    st.caption("These look like plausible values (for example a mistyped state code), so no simple rule proves them wrong.")

with tab4:
    st.markdown(
        """
**Method.** The checker looks only at the dirty table. The clean table is used only to score it.

- **Format rules:** ZIP and provider number are 5 digits, phone is 10 digits, score is a percentage, sample is "N patients".
- **Consistency rules:** values that should be the same for a key (provider number, measure code) must agree. A cell that differs from its group's majority is flagged and the majority value is proposed as the fix.
- **Shape profiling** was tested and left out because it added false alarms.

**Limitations.**
- The rules were written after inspecting this dataset, so the results are optimistic and specific to this table.
- Consistency checks need repeated entities (many rows per provider).
- Score and sample cells can be flagged but not repaired, since their values differ from row to row.
        """
    )
