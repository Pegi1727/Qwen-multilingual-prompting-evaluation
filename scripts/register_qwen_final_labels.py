import pandas as pd
from pathlib import Path
correct='101 104 106 111 112 113 121 131 132 133 134 136 139 141 144 160 161 171 172 173 174 181 191 194 196 201 205 207 210 211 214 216 217 224 227 230 231 234 240 241 244 247 250 251 252 254 257 260 261 264 267 270 271 274 276 277 280 281 284 286 287 290 291 292 293 294 296 297 300 301 304 307 310 311 314 317 320 321 322 324 326 330 331 334 336 337 339 340 341 342 344 347 350 351 354 358 360 361 364 367 370 374 379 384 390 391 394 397 404 434 436 441 454 455 467 470 500 507 510 552 554 557 560 564 570 580 584 600'
mixed='105 107 108 110 117 120 127 130 137 138 147 151 167 175 177 180 184 187 190 197 200 237 327 377 380 407 411 413 427 437 447 487 565 567 577 587'
unclear='102 115 125 128 135 140 145 148 150 155 157 165 178 185 188 195 198 212 218 238 302 352 408 410 418 420 425 428 430 438 440 448 450 458 460 468 488 498 508 515 517 518 520 525 528 530 535 538 540 548 550 568 588 590 595 598'
groups={label:set(map(int,nums.split())) for label,nums in [('درست',correct),('ترکیبی',mixed),('نامفهوم',unclear)]}
assert sum(map(len,groups.values()))==len(set.union(*groups.values()))
assert all(101<=n<=600 for s in groups.values() for n in s)
rows=[{'review_number':n,'user_content_label':next((k for k,s in groups.items() if n in s),'غلط'),'label_source':'user_final_revision','format_compliance':'not_evaluated'} for n in range(101,601)]
df=pd.DataFrame(rows)
p=Path('/mnt/data/qwen_labels_101_600_final.csv');df.to_csv(p,index=False,encoding='utf-8-sig')
print(df.user_content_label.value_counts().to_string())
print('rows',len(df),'unique',df.review_number.nunique())
print('FIRST100 COLUMNS',pd.read_csv('/mnt/data/qwen_first100_review_revised.csv').columns.tolist())
