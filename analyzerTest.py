from modules.directivesAnalyzer import DirectivesAnalyzer

directivesAnalyzer = DirectivesAnalyzer(
    "./output/Machsuite-GEMM-NCubed", 
    0
)
directivesAnalyzer.analyze()