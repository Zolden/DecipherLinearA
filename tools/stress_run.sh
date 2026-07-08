#!/bin/bash
# Стресс-тест воспроизводимости: прогон всех автономных скриптов на чистом клоне.
cd "$(dirname "$0")/.."
PY=.venv/Scripts/python.exe
export PYTHONIOENCODING=utf-8
export PYTHONHASHSEED=0
FAIL=0
run() {
  s=$1; log=$2
  if [ -n "$log" ]; then
    $PY "$s" > "$log" 2>&1 || { echo "CRASH: $s"; FAIL=1; }
  else
    $PY "$s" > /dev/null 2>&1 || { echo "CRASH: $s"; FAIL=1; }
  fi
  echo "done: $s"
}
run validate_pkl.py validate_pkl.log
run parse_underdots.py underdots_run.log
run analyze_underdot_arith.py underdot_arith.log
run analyze_transaction_signs.py transaction_signs.log
run analyze_alternations.py alternations.log
run analyze_positions.py positions.log
run analyze_homographs.py homographs.log
run analyze_semantics.py semantics.log
run analyze_scribes.py scribes.log
run analyze_toponyms.py toponyms.log
run analyze_suffix_function.py suffix_function.log
run analyze_unknown_signs.py unknown_signs.log
run analyze_libation_slots.py libation_slots.log
run analyze_segmentation.py segmentation.log
run analyze_markers_replication.py markers_replication.log
run analyze_underdot_robustness.py underdot_robustness.log
run analyze_prefix_a.py prefix_a.log
run analyze_sign118.py sign118.log
run analyze_qa.py qa_anomaly.log
run analyze_lb_names.py lb_names.log
run analyze_lb_names2.py lb_names2.log
run analyze_segmentation2.py segmentation2.log
run analyze_dikite.py dikite.log
run analyze_fractions.py fractions_part.log
run analyze_typology.py typology.log
run analyze_name_candidates.py name_candidates.log
run analyze_onomasticon3.py onomasticon3.log
run analyze_onomasticon4.py onomasticon5.log
run analyze_metrology2.py metrology2.log
run analyze_slots2_expand.py slots2_expand.log
run analyze_contrasts.py contrasts.log
run analyze_contrasts2.py contrasts2.log
run analyze_prefix_i.py prefix_i.log
run analyze_ida.py ida.log
run analyze_adu.py adu.log
run analyze_adu2.py adu2.log
run analyze_qe.py qe.log
run analyze_religious_network.py religious_network.log
run analyze_sign_hints.py sign_hints.log
run analyze_crossword.py crossword.log
run analyze_118_value.py value118.log
run analyze_sasara.py sasara.log
run analyze_sasara2.py sasara2.log
run analyze_slot2_lb.py slot2_lb.log
run analyze_operators.py operators.log
run analyze_cm.py cm.log
run formula_template.py formula_template.log
# этапы 13–16. Вне ростера: typology_families*/lb-парсеры (сетевые кэши);
# analyze_onomasticon6.py читает lb2_*.tsv — их детерминированно восстанавливает
# parse_lbxyz.py из кэша .lbxyz_cache.js (tools/fetch_lbxyz.sh, pin 84e0b00e)
run analyze_slot1.py slot1.log
run analyze_aromatics.py aromatics.log
run analyze_bimorphs.py bimorphs.log
run analyze_onomasticon6.py onomasticon6.log
run analyze_morphotactics.py morphotactics.log
run analyze_cult_bridge.py cult_bridge.log
run analyze_anchors.py anchors.log
run analyze_operator_typology.py operator_typology.log
run analyze_rare_signs.py rare_signs.log
# этап 17. parse_sigla.py вне ростера (кэш .sigla_cache.js гитигнорен,
# восстанавливается tools/fetch_sigla.sh); analyze_diachrony.py читает
# его закоммиченный выход sigla_docs.tsv
run analyze_diachrony.py diachrony.log
run analyze_record_syntax.py record_syntax.log
run analyze_crossword3.py crossword3.log
run analyze_onomasticon8.py onomasticon8.log
run analyze_suffix_complementarity.py suffix_complementarity.log
# этап 18. parse_sigla_signs.py вне ростера (кэш .sigla_cache.js);
# analyze_formula_dated.py читает закоммиченный sigla_docs.tsv
run analyze_headers.py headers.log
run analyze_onomasticon9.py onomasticon9.log
run analyze_formula_dated.py formula_dated.log
# этап 19 (analyze_divergences.py читает закоммиченный sigla_signs.tsv)
run analyze_final_alternation.py final_alternation.log
run analyze_divergences.py divergences.log
run analyze_topic_class.py topic_class.log
run analyze_crossword4.py crossword4.log
# этап 20 (analyze_source_check.py вне ростера: читает corpus_raw.json,
# восстановимый tools/fetch_sources.sh)
run analyze_o_rule_strata.py o_rule_strata.log
run analyze_internal_alternation.py internal_alternation.log
echo "FAIL=$FAIL"
echo STRESS_DONE
