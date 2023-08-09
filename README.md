# texplora-assignment

### Task 1
Given a CSV file with several transactions, find the recurrent transactions based on 'reference, payable and receivable amount' and provide an output indicating the 'Plan' of the recurring transaction basis it's frequency.

- Plans could be -
	- Daily (recurring within 1 to 3 days period)
	- Weekly (recurring within 5 to 9 days period)
	- Monthly (recurring within 25 to 35 days period)
	- Others (recurring, but irregularly)
	*The check is not strict and buffer is considered. Hence 1-3 days, 5-9 days and so on*
- Adjustments for transactions occurring on weekend and holidays have been made.
- Transactions with amount < 1 Euro have been skipped as they could be payment verifications and other insignificant miscellaneous transactions
- Transactions with reference "Ripresa saldo esercizio precedente" have been skipped
- Unique account (branch code) has been considered

#### Open Questions
- What about duplicate transactions which are occurring the same day? Can those be ignored as payments by mistake?
- Say a transaction is almost recurrent but 1-2 transactions are off, making it a non-pattern. Shall we look for outliers? This could be an enhancement
- Will a defined list of holidays be provided?
---

### Task 2
Given an unsorted integer array nums, return the smallest missing positive integer. 

**Approach:** Sort and iteratively find the smallest number  
**Sort TC:** O(n log n)  
**Search TC:** O(n)  
**Overall TC:** O(n log n)  
**Overall SC:** O(1)

Unittests have been written for the method.
