from __future__ import division, print_function
import argparse
import collections
import sys
import math


parser = argparse.ArgumentParser(
  description="Demo doc-MRT vs seq-MRT scoring for a set of reference sentences and sampled translations." 
  " Running without arguments uses demo sentences. Both --references and --samples filepaths must be set"
  " to use your own references and sample candidates. No text preprocessing is done in script.")
parser.add_argument("-N", default=3, type=int,
                    help="Number of samples per sentence")
parser.add_argument("--references", default=None, 
                    help="File containing reference sentences if not using demo references.")
parser.add_argument("--samples", default=None,
                    help="File containing args.N samples for each reference if not using demo samples.")
parser.add_argument("--print_per_sample_scores", default=False, action='store_true',
                    help="Set if printing a score for each individual sample (as would be used for MRT)")
args = parser.parse_args()


def count_ngram_segment(segment, max_order):
  ngram_counts = collections.Counter()
  for order in range(1, max_order + 1):
    for i in range(0, len(segment) - order + 1):
      ngram = tuple(segment[i:i + order])
      ngram_counts[ngram] += 1
  return ngram_counts

def score_bleu_many(refs, hyps, max_order=4, use_bp=True, do_smooth=True):
  ref_length = 0
  hyp_length = 0
  matches_by_order = [0] * max_order
  hyps_by_order = [0] * max_order
  for (ref, hyp) in zip(refs, hyps):
    ref_length += len(ref)
    hyp_length += len(hyp)
    ref_ngram_counts = count_ngram_segment(ref, max_order)
    hyp_ngram_counts = count_ngram_segment(hyp, max_order)
    overlap = dict((ngram, min(count, hyp_ngram_counts[ngram]))
                   for ngram, count in ref_ngram_counts.items())
    for ngram in overlap:
      matches_by_order[len(ngram) - 1] += overlap[ngram]
    for ngram in hyp_ngram_counts:
      hyps_by_order[len(ngram)-1] += hyp_ngram_counts[ngram]
  bleu = score_matches(matches_by_order, hyps_by_order, max_order, do_smooth)
  if use_bp:
    ratio = hyp_length / ref_length
    bp = math.exp(1 - 1. / ratio) if ratio < 1.0 else 1.0
    bleu *= bp
  return bleu


def score_matches(matches_by_order, hyps_by_order, max_order, do_smooth):
  precisions = [0] * max_order
  smooth = 1
  for i in range(0, max_order):
    if hyps_by_order[i] > 0:
      if matches_by_order[i] > 0 or not do_smooth:
        precisions[i] = matches_by_order[i] / hyps_by_order[i]
      else:
        smooth *= 2
        precisions[i] = 1.0 / (smooth * hyps_by_order[i])
    else:
      precisions[i] = 0.0
  geo_mean = 0.0
  if max(precisions) > 0:
    p_log_sum = sum(math.log(p) for p in precisions if p)
    geo_mean = math.exp(p_log_sum/max_order)
  return geo_mean

references = ["this is an example", "so is this"]
samples = [["this example", "example", "this is example"],
           ["so", "so so is this", "is this"]]
if args.references is not None and args.samples is not None:
  references = []
  samples = [[]]
  with open(args.references) as fr:
    for line in fr:
      references.append(line.strip())
  with open(args.samples) as fs:
    for line in fs:
      if len(samples[-1]) == args.N:
        samples.append([])
      samples[-1].append(line.strip())
  if len(samples) != len(references):
    sys.exit("ERROR: need args.N samples for each reference")

"""
For sBLEU, just score each reference/source individually
"""
print('\nSeq-MRT\n')
for idx, r in enumerate(references):
  for s in samples[idx]:
    sbleu = score_bleu_many([r], [s])
    if args.print_per_sample_scores:
      print(f'{sbleu}\t{s}')
    else: 
      print(f'sBLEU for seq-MRT:{sbleu}\treference: {r}\tsample: {s}')


"""
For doc-MRT, group samples for all sentences into documents, and score them together
"""
print('\nRandom Doc-MRT\n')
doc_scores = []
for idx in range(args.N):
  sample_doc = []
  for sample_set in samples:
    sample_doc.append(sample_set[idx])
  docbleu = score_bleu_many(references, sample_doc)
  if args.print_per_sample_scores:
    doc_scores.append(docbleu)
  else: 
    print(f'BLEU for random doc-MRT: {docbleu}\treference: {references}\tsample: {sample_doc}')

if args.print_per_sample_scores:
  for idx in range(len(references)):
    for s_idx, s in enumerate(samples[idx]):
      print(f'{doc_scores[s_idx]}\t{s}')
    

"""
For ordered doc-MRT, group samples as before, but sort them first 
Here we sort by sBLEU, but we could sort by ngram overlap, likelihood, or even length
"""
print('\nOrdered Doc-MRT\n')
ordered_samples_idx = []
doc_scores = []
for idx, r in enumerate(references):
  scores = []
  for s in samples[idx]:
    scores.append(score_bleu_many([r], [s]))
  ordered_samples_idx.append([x for x, _ in sorted(zip(range(args.N), scores),
                                                   key=lambda x: x[1], reverse=True)])
for idx in range(args.N):
  sample_doc = []
  for set_idx, sample_set in enumerate(ordered_samples_idx):
    sample_doc.append(samples[set_idx][sample_set[idx]])
  docbleu = score_bleu_many(references, sample_doc)
  if args.print_per_sample_scores:
    doc_scores.append(docbleu)
  else: 
    print(f'BLEU for ordered doc-MRT: {docbleu}\treference: {references}\tsample: {sample_doc}')
if args.print_per_sample_scores:
  for idx in range(len(references)):
    for s_idx, s in enumerate(samples[idx]):
      print(doc_scores[ordered_samples_idx[idx].index(s_idx)], s)

    


  
