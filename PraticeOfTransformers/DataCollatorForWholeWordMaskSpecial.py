﻿# -*- coding: utf-8 -*-
import random
import warnings
from dataclasses import dataclass

from typing import Any, Optional, Tuple, Mapping, List, Union, Dict

import numpy as np
from transformers import PreTrainedTokenizerBase, BertTokenizer, BertTokenizerFast
from transformers.data.data_collator import DataCollatorMixin, tolist, DataCollatorForLanguageModeling

from PraticeOfTransformers.DataCollatorForLanguageModelingSpecial import DataCollatorForLanguageModelingSpecial


@dataclass
class DataCollatorForWholeWordMaskSpecial(DataCollatorForLanguageModelingSpecial):
    """
    Data collator used for language modeling that masks entire words.

    - collates batches of tensors, honoring their tokenizer's pad_token
    - preprocesses batches for masked language modeling

    <Tip>

    This collator relies on details of the implementation of subword tokenization by [`BertTokenizer`], specifically
    that subword tokens are prefixed with *##*. For tokenizers that do not adhere to this scheme, this collator will
    produce an output that is roughly equivalent to [`.DataCollatorForLanguageModeling`].

    </Tip>"""

    """
        Data collator used for language modeling that masks entire words.

        - collates batches of tensors, honoring their tokenizer's pad_token
        - preprocesses batches for masked language modeling

        <Tip>

        This collator relies on details of the implementation of subword tokenization by [`BertTokenizer`], specifically
        that subword tokens are prefixed with *##*. For tokenizers that do not adhere to this scheme, this collator will
        produce an output that is roughly equivalent to [`.DataCollatorForLanguageModeling`].

        </Tip>"""

    def torch_call(self, examples: List[Union[List[int], Any, Dict[str, Any]]]) -> Dict[str, Any]:
        examples,kyewords=list(zip(*examples))  #更改过源码，进行mask的时候已经变成list（tuple（））
        examples=list(examples) #更改过源码 转为list
        kyewords=list(kyewords) #更改过源码 转为list

        if isinstance(examples[0], Mapping):
            input_ids = [e["input_ids"] for e in examples]
        else:
            input_ids = examples
            examples = [{"input_ids": e} for e in examples]

        batch_input = self._torch_collate_batch(examples=input_ids, tokenizer=self.tokenizer, pad_to_multiple_of=self.pad_to_multiple_of)

        mask_labels = []
        for e,k in zip(examples,kyewords):
            ref_tokens = []
            kw_tokens = [] #是个二维数组，每一条句子中 会有多个keyword
            for id in tolist(e["input_ids"]):
                # token = self.tokenizer.convert_ids_to_tokens(id)
                token = self.tokenizer._convert_id_to_token(id)
                ref_tokens.append(token)
            for k_id in k:
                k_token = self.tokenizer.convert_ids_to_tokens(k_id)
                kw_tokens.append(k_token)

            # For Chinese tokens, we need extra inf to mark sub-word, e.g [喜,欢]-> [喜，##欢]
            #目前这里目前  没用到过
            if "chinese_ref" in e:
                ref_pos = tolist(e["chinese_ref"])
                len_seq = len(e["input_ids"])
                for i in range(len_seq):
                    if i in ref_pos:
                        ref_tokens[i] = "##" + ref_tokens[i]
            mask_labels.append(self._whole_word_mask(input_tokens=ref_tokens,kw_tokens=kw_tokens))
        #对于subword的单词及逆行mask
        batch_mask = self._torch_collate_batch(examples=mask_labels, tokenizer=self.tokenizer, pad_to_multiple_of=self.pad_to_multiple_of)
        inputs, labels = self.torch_mask_tokens(batch_input, batch_mask)
        return {"input_ids": inputs, "labels": labels}





    def _whole_word_mask(self, input_tokens: List[str],kw_tokens: List[str], max_predictions=512):
        """
        Get 0/1 labels for masked tokens with whole word mask proxy
        """
        if not isinstance(self.tokenizer, (BertTokenizer, BertTokenizerFast)):
            warnings.warn(
                "DataCollatorForWholeWordMask is only suitable for BertTokenizer-like tokenizers. "
                "Please refer to the documentation for more information."
            )


        '''
        这一块的逻辑需要更改，将关键词转为一个词，关键词要么整个被选中，要么不被选中
        '''
        #先处理keyword
        keyword_start_all_index=self.get_index_in_array(be_search_array=input_tokens, target_array=kw_tokens)
        post_tokens=[]
        post_index=[]
        curr_index=0
        while(curr_index<len(input_tokens)):
            if (curr_index,curr_index+len(kw_tokens)) not in keyword_start_all_index: #keyword_start_all_index 返回时[（star,end）]
                post_tokens.append([input_tokens[curr_index]])
                post_index.append([curr_index])
                curr_index+=1
            else:
                post_tokens.append([_ for _ in  input_tokens[curr_index:curr_index+len(kw_tokens)]])
                post_index.append([_ for _ in  range(curr_index,curr_index+len(kw_tokens))])
                curr_index+=len(kw_tokens)


        # 在处理subword
        cand_indexes = []
        for  index_arr,token_arr in zip(post_index,post_tokens):
            if len(token_arr)==1 and (token_arr[0] == "[CLS]" or token_arr[0] == "[SEP]"):
                continue
            #对于涉及到关键词的直接添加了，因为如果input被分为多个subword，那么关键词肯定也会被分成subword，所以不用考虑后面的
            if len(token_arr)!=1:
                cand_indexes.append(index_arr)
                continue
            if len(cand_indexes) >= 1 and token_arr[0].startswith("##"):
                cand_indexes[-1].append(index_arr[0])
            else:
                cand_indexes.append(index_arr)

        random.shuffle(cand_indexes)
        num_to_predict = min(max_predictions, max(1, int(round(len(input_tokens) * self.mlm_probability))))
        masked_lms = []
        covered_indexes = set()
        for index_set in cand_indexes:
            if len(masked_lms) >= num_to_predict:
                break
            # If adding a whole-word mask would exceed the maximum number of
            # predictions, then just skip this candidate.
            if len(masked_lms) + len(index_set) > num_to_predict:
                continue
            is_any_index_covered = False
            for index in index_set:
                if index in covered_indexes:
                    is_any_index_covered = True
                    break
            if is_any_index_covered:
                continue
            for index in index_set:
                covered_indexes.add(index)
                masked_lms.append(index)

        if len(covered_indexes) != len(masked_lms):
            raise ValueError("Length of covered_indexes is not equal to length of masked_lms.")
        mask_labels = [1 if i in covered_indexes else 0 for i in range(len(input_tokens))]
        return mask_labels

    def torch_mask_tokens(self, inputs: Any, mask_labels: Any) -> Tuple[Any, Any]:
        """
        Prepare masked tokens inputs/labels for masked language modeling: 80% MASK, 10% random, 10% original. Set
        'mask_labels' means we use whole word mask (wwm), we directly mask idxs according to it's ref.
        """
        import torch

        if self.tokenizer.mask_token is None:
            raise ValueError(
                "This tokenizer does not have a mask token which is necessary for masked language modeling. Remove the"
                " --mlm flag if you want to use this tokenizer."
            )
        labels = inputs.clone()
        # We sample a few tokens in each sequence for masked-LM training (with probability args.mlm_probability defaults to 0.15 in Bert/RoBERTa)

        probability_matrix = mask_labels

        special_tokens_mask = [
            self.tokenizer.get_special_tokens_mask(val, already_has_special_tokens=True) for val in labels.tolist()
        ]
        probability_matrix.masked_fill_(torch.tensor(special_tokens_mask, dtype=torch.bool), value=0.0)
        if self.tokenizer._pad_token is not None:
            padding_mask = labels.eq(self.tokenizer.pad_token_id)
            probability_matrix.masked_fill_(padding_mask, value=0.0)

        masked_indices = probability_matrix.bool()
        labels[~masked_indices] = -100  # We only compute loss on masked tokens

        # 80% of the time, we replace masked input tokens with tokenizer.mask_token ([MASK])
        indices_replaced = torch.bernoulli(torch.full(labels.shape, 0.8)).bool() & masked_indices
        inputs[indices_replaced] = self.tokenizer.convert_tokens_to_ids(self.tokenizer.mask_token)

        # 10% of the time, we replace masked input tokens with random word
        indices_random = torch.bernoulli(torch.full(labels.shape, 0.5)).bool() & masked_indices & ~indices_replaced
        random_words = torch.randint(len(self.tokenizer), labels.shape, dtype=torch.long)
        inputs[indices_random] = random_words[indices_random]

        # The rest of the time (10% of the time) we keep the masked input tokens unchanged
        return inputs, labels



    def _torch_collate_batch(self,examples, tokenizer, pad_to_multiple_of: Optional[int] = None):
        """Collate `examples` into a batch, using the information in `tokenizer` for padding if necessary."""
        import torch

        # Tensorize if necessary.
        if isinstance(examples[0], (list, tuple, np.ndarray)):
            examples = [torch.tensor(e, dtype=torch.long) for e in examples]

        length_of_first = examples[0].size(0)

        # Check if padding is necessary.

        are_tensors_same_length = all(x.size(0) == length_of_first for x in examples)
        if are_tensors_same_length and (pad_to_multiple_of is None or length_of_first % pad_to_multiple_of == 0):
            return torch.stack(examples, dim=0)

        # If yes, check if we have a `pad_token`.
        if tokenizer._pad_token is None:
            raise ValueError(
                "You are attempting to pad samples but the tokenizer you are using"
                f" ({tokenizer.__class__.__name__}) does not have a pad token."
            )

        # Creating the full tensor and filling it with our data.
        max_length = max(x.size(0) for x in examples)
        if pad_to_multiple_of is not None and (max_length % pad_to_multiple_of != 0):
            max_length = ((max_length // pad_to_multiple_of) + 1) * pad_to_multiple_of
        result = examples[0].new_full([len(examples), max_length], tokenizer.pad_token_id)
        for i, example in enumerate(examples):
            if tokenizer.padding_side == "right":
                result[i, : example.shape[0]] = example
            else:
                result[i, -example.shape[0]:] = example
        return result







    def get_index_in_array(self,be_search_array,target_array):
            a = be_search_array
            bs = target_array

            find_all_index = []
            #应对多个keyword，也就是多个关键词
            for b in bs:
                index = 0
                while (index < len(a)):
                    #当两个数组形式对比的时候，有一个为ndraay 需要用到.all() 如果是两个纯array则不需要
                    if a[index] == b[0] and (index + len(b)) <= len(a) and (a[index:index + len(b)] == b[:]):
                        find_all_index.append((index, index + len(b)))
                        index += len(b)
                    else:
                        index += 1
            return find_all_index