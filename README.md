# context-minimum-risk-training
Minimum Risk Training with context demo for the paper [Using Context in Neural Machine Translation Training Objectives](https://www.aclweb.org/anthology/2020.acl-main.693.pdf) (ACL 2020)


## Summary 

The paper introduces a variation on Minimum Risk Training (MRT) which groups samples in a minibatch into a `document' context. If each sample appears in one context, the objective function simplifies to be as for regular MRT, but with a different scoring function. This demo illustrates that scoring function.

Sequence-level MRT (seq-MRT) would score sentences individually, often according to sentence-level BLEU (sBLEU):
```
sBLEU for seq-MRT:0.554788268632133     reference: this is an example   sample: this example
sBLEU for seq-MRT:0.20774818714360088   reference: this is an example   sample: example
sBLEU for seq-MRT:0.7667526145229728    reference: this is an example   sample: this is example
sBLEU for seq-MRT:0.01831563888873418   reference: so is this   sample: so
sBLEU for seq-MRT:0.7361703354503866    reference: so is this   sample: so so is this
sBLEU for seq-MRT:0.6514390575310556    reference: so is this   sample: is this
```

However document-level MRT (doc-MRT) groups sentences into documents for scoring. Grouping randomly simply smooths the scores:

```
BLEU for random doc-MRT: 0.33649609457427737    reference: ['this is an example', 'so is this'] sample: ['this example', 'so']
BLEU for random doc-MRT: 0.5496846785044786     reference: ['this is an example', 'so is this'] sample: ['example', 'so so is this']
BLEU for random doc-MRT: 0.7258588356307976     reference: ['this is an example', 'so is this'] sample: ['this is example', 'is this']
```




If the samples are ordered before grouping into documents, scores indicate more context for which samples are better overall.
```
BLEU for ordered doc-MRT: 0.8444916600635684    reference: ['this is an example', 'so is this'] sample: ['this is example', 'so so is this']
BLEU for ordered doc-MRT: 0.5870202574789813    reference: ['this is an example', 'so is this'] sample: ['this example', 'is this']
BLEU for ordered doc-MRT: 0.12110333239232977   reference: ['this is an example', 'so is this'] sample: ['example', 'so']

```




## Use

The simplest way to run the demo is using the inbuilt examples, as above:
```
python demo.py
```

The demo can also be run with your own files of reference translations and samples - there must be the same number of samples N for each sentence.
```
python demo.py --samples=demo_samples --references=demo_references -N=3
```

If you wish to see the score for each sample individually under the different schemes, the --print_per_sample_scores flag can be used with either setting:

```
python demo.py --print_per_sample_scores

Seq-MRT

0.554788268632133       this example
0.20774818714360088     example
0.7667526145229728      this is example
0.01831563888873418     so
0.7361703354503866      so so is this
0.6514390575310556      is this

Random Doc-MRT

0.33649609457427737     this example
0.5496846785044786      example
0.7258588356307976      this is example
0.33649609457427737     so
0.5496846785044786      so so is this
0.7258588356307976      is this

Ordered Doc-MRT

0.5870202574789813 this example
0.12110333239232977 example
0.8444916600635684 this is example
0.12110333239232977 so
0.8444916600635684 so so is this
0.5870202574789813 is this

```


## Citing


```
@inproceedings{saunders-etal-2020-using,
    title = "Using Context in Neural Machine Translation Training Objectives",
    author = "Saunders, Danielle  and
      Stahlberg, Felix  and
      Byrne, Bill",
    booktitle = "Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics",
    month = jul,
    year = "2020",
    address = "Online",
    publisher = "Association for Computational Linguistics",
    url = "https://www.aclweb.org/anthology/2020.acl-main.693",
    doi = "10.18653/v1/2020.acl-main.693",
    pages = "7764--7770",
    abstract = "We present Neural Machine Translation (NMT) training using document-level metrics with batch-level documents. Previous sequence-objective approaches to NMT training focus exclusively on sentence-level metrics like sentence BLEU which do not correspond to the desired evaluation metric, typically document BLEU. Meanwhile research into document-level NMT training focuses on data or model architecture rather than training procedure. We find that each of these lines of research has a clear space in it for the other, and propose merging them with a scheme that allows a document-level evaluation metric to be used in the NMT training objective. We first sample pseudo-documents from sentence samples. We then approximate the expected document BLEU gradient with Monte Carlo sampling for use as a cost function in Minimum Risk Training (MRT). This two-level sampling procedure gives NMT performance gains over sequence MRT and maximum-likelihood training. We demonstrate that training is more robust for document-level metrics than with sequence metrics. We further demonstrate improvements on NMT with TER and Grammatical Error Correction (GEC) using GLEU, both metrics used at the document level for evaluations.",
}
	    ```
	    
