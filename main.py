import os
import openai
import json
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()


class SummaryInput(BaseModel):
    summary: str


def generate_clinical_history(summary: str) -> str:
    initial_prompt = "你是一個中醫師助理，請將以下內容轉變成病史。 切記內容要準確，不可以擅自增添內容，用字要用標準的病史寫法，要用繁體字：\n————————————\n列表：\n- 入院前兩日唔小心受涼\n- 有咽喉痛、鼻塞\n- 陣發性非刺激性咳嗽，較劇烈\n- 黃綠色痰，量少，難咳出\n- 輕度畏寒\n- 全身酸痛唔舒服\n- 冇寒顫、高燥、頭暈、心跳加速\n- 冇腹痛腹瀉\n- 未經任何處理\n- 之前無好轉，來求診並入院\n病史：\n主訴:咽痛鼻塞咳嗽2天\n現病史：入院前2天不慎受涼後,出現咽痛、鼻塞,繼而出現咳嗽,呈陣發性非刺激性,較劇烈,痰呈黃綠色,量少,難咯,並感輕度畏寒,全身酸痛不適,無寒戰高熱,無頭暈頭痛,無胸悶心悸,無腹痛腹瀉等,未予注意,未經任何處理,經休息上述病情無好轉,今求診我院;\n——————————————\n列表：\n- 上腹部脹痛兩日\n- 飲食不節後出現病症\n- 持續痛楚，飯後更甚\n- 不想進食\n- 有時感到噁心想嘔\n- 沒有畏寒發燒\n- 沒有頭暈頭痛\n- 沒有胸悶心悸\n- 沒有腹瀉黑便等\n- 曾到當地診所就診\n- 服藥後未見改善，遂來本院\n病史：\n主訴:上腹脹痛2天\n現病史：入院前2天飲食不節後,出現上腹脹痛,呈持續性,餐後尤甚,致不思飲食,時有噁心欲吐,無畏冷發熱,無頭暈頭痛,無胸悶心悸,無腹瀉黑便等,就診於當地診所,予“藥物口服” 具體用藥欠祥,上述病情無好轉,今求診我院;\n————————————————\n列表：\n- 上腹脹痛兩日\n- 食物不潔感覺\n- 臍周痛，持續性\n- 腹瀉黃水樣，粘液，每日超過10次\n- 洩瀉後腹痛稍緩解\n- 肛門灼熱感\n- 時有噁心嘔吐\n- 無畏冷發熱\n- 無眩暈頭痛\n- 無胸悶心悸\n- 無黑便\n- 曾就醫並服藥，但具體情況未知\n- 病情有改善，就診本院\n病史：\n主訴:上腹脹痛2天\n現病史：入院前2天飲食不潔後,出現腹痛,以臍周為主,呈持續性隱痛,陣發性加劇,同時出現腹瀉,呈黃色浠水樣,夾有粘液,日10餘次,洩後腹痛稍緩解,伴肛門灼熱感,時有噁心欲吐,無畏冷發熱,無頭暈頭痛,無胸悶心悸,無黑便等,就診於當地診所,予“藥物口服” 具體用藥欠祥,上述病情稍好轉,今求診我院;"

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {"role": "system", "content": initial_prompt},
            {"role": "user", "content": summary},
        ],
        temperature=0,
    )
    return response.choices[0].message


def generate_differential_diagnosis(summary: str) -> str:
    initial_prompt = "你是一個家庭醫學專家，請使用你的知識，輔助基層中醫，讓他們提供更全面的診療思路。\n\n請參考病例重點， 提出疾病初步診斷以及鑒別診斷以及鑒別診斷所需的資訊或檢查\n\n請以以下方式輸出：\n初步診斷: {初步診斷} :\n鑒別診斷：\n1. {鑒別診斷1} ： {所需資訊或檢查1}\n2. {鑒別診斷2} ： {所需資訊或檢查2}\n1. {鑒別診斷3} ： {所需資訊或檢查3}"
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": initial_prompt},
            {"role": "user", "content": summary},
        ],
        temperature=0,
    )
    return response.choices[0].message


def generate_tcm_advice(summary: str) -> str:
    initial_prompt = "你是一個老中醫，請使用你的知識，輔助基層中醫，讓他們提供更全面的診療思路。\n\n請參考病例重點， 提出診斷，鑒別診斷，以及辯證要點\n\n請以以下方式輸出：\n初步診斷: {初步診斷} :\n鑒別診斷：\n1. {鑒別診斷1} ： {所需資訊或檢查1}\n2. {鑒別診斷2} ： {所需資訊或檢查2}\n3. {鑒別診斷3} ： {所需資訊或檢查3}"
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": initial_prompt},
            {"role": "user", "content": summary},
        ],
        temperature=0,
    )
    return response.choices[0].message


def generate_obgyn_history(summary: str) -> str:
    initial_prompt = "你是一個中醫師助理，請將以下內容轉變成病史。切記內容要準確，不可以擅自增添內容，，，要用繁體字：\n\n參考以下案例”“”\n總結1：\n- 這次月經來晚了10天\n- 這次月經來於2010年11月11日\n- 月經量比較少，三日結束\n- 月經暗色暗紅，質地稀，有血塊\n- 來月經史肚痛，腰痛\n- 來M前胸脹\n- 平時煩躁容易生氣\n- 三次懷孕，都流產，無生過\n- 三次都是藥物流產\n\n病史1：\n主訴：月經週期推後10天。\n病史：平素月經週期規律，天。本次月經週期推後十天，lmp\n2010年11月11號，pmp2010年10月1號。經量偏少，三天干淨。經色暗紅。經質偏稀，有血塊。經行伴有小腹疼痛，腰骶墜痛感。經前有乳房脹痛。煩躁易怒，畏寒肢冷，面色恍白。食慾減退，無噁心嘔吐。平素月經量可，經期為4到5天。經色紅，無血塊。無經行腹痛及腰骶墜痛感。經前偶有乳房脹痛。白帶色質量味均正常。\n有性生活史。 G3P0A3L0。三次流產均為藥物流產，流產後B超檢查提示流產乾淨。現工具避孕。\n否認盆腔炎、陰道炎病史。\n\n總結2：\n- 腰尾骨疼痛3個月，加重於累和性交後\n- 陰道分泌物增多，外陰癢\n- 性交後出血\n- 尿頻、尿急、尿痛\n- 尿液顏色偏黃，有時像醬油色\n-上次月經2011年5月3號，這次月經2011-6-10\n- 月經週期晚7天左右，月經量少，顏色偏淡\n- 情緒低落，容易激動\n- 懷孕3次，生1個，2次藥流\n- 使用節育環避孕\n- 曾患細菌性陰道炎，已治愈\n- 2008年因子宮肌瘤手術\n-無食物藥物過敏\n- 胃口不好，睡眠一般，大便正常，小便顏色偏紅，尿次數多\n- 舌頭胖，有牙齒印子，舌苔薄黃，脈搏濡緩\n\n病史2：\n主訴：腰骶酸痛3個月，加重伴尿頻、尿急、尿痛4天。\n現病史：患者3月前出現無明顯誘因的非經期腰骶酸痛，勞累、性交後加重。 2月前出現陰道分泌物增多，間有外陰瘙癢，性交後出血。自服宮炎康膠囊，效果不顯。 4天前出現尿頻、尿急、尿痛，伴有小便色黃，偶可呈醬油色。自服阿莫西林膠囊治療，療效不顯。患者自發病以來，神疲乏力，食慾減退。\n患者平素月經不規律，月經週期一般推後7天左右，3-4天/30-36天，經量偏少，經色偏淡，無血塊，無經期腹痛、腰酸痛、乳房脹痛。間有情緒抑鬱，易激動。 Lmp2011-6-10,pmp2011-5-03。\n平素白帶量可，色白質稀，無異味。\n適齡結婚，孕3產1，兩次流產均為藥物流產，流產後B超顯示流產乾淨。育有一子，體健。現節育環避孕。曾有細菌性陰道炎病史，甲硝唑治療後未再复發。 2008曾因子宮肌瘤行手術切除治療。否認食物藥物過敏史。\n納差，眠尚，大便可，小便短赤，次頻。舌胖，邊有齒痕，苔薄黃，脈濡緩。\n\n總結3：\n-外陰癢和陰道分泌物增多已有兩個月\n-陰道分泌物黃綠色，稀薄泡沫狀，有臭味\n-偶爾疼痛和灼熱感\n-下腹部有時酸痛，性交後尤甚\n-情緒不好，精神不振，食慾不佳\n-月經週期30天，持續4-5天，量多，顏色偏暗，偶爾有血塊\n-上次月經2011年6月20日，前次月經2011年5月19日\n-白帶量正常，質地粘稠，白色略透明，無異味\n-生過兩個孩子，一次藥物流產，流產後B超檢查乾淨\n-採用工具避孕\n-兩年前患真菌性陰道炎，抗真菌治療後未復發\n-胃口不好，睡眠不佳，大便粘膩，小便顏色偏紅\n-舌紅，舌苔黃膩，脈搏滑數\n\n病史3：\n病史：\n主訴：外陰瘙癢和陰道分泌物增多已有兩個月。\n現病史：患者兩個月前出現外陰瘙癢和陰道分泌物增多，分泌物為黃綠色，稀薄泡沫狀，有臭味，偶爾伴有疼痛和灼熱感。下腹部有時酸痛，性交後尤甚。患者情緒不好，精神不振，食慾不佳。月經週期為30天，持續4-5天，量多，顏色偏暗，偶爾有血塊。上次月經為2011年6月20日，前次月經為2011年5月19日。白帶量正常，質地粘稠，白色略透明，無異味。患者生過兩個孩子，一次藥物流產，流產後B超檢查乾淨，現採用工具避孕。兩年前患真菌性陰道炎，抗真菌治療後未復發。患者胃口不好，睡眠不佳，大便粘膩，小便顏色偏紅。舌紅，舌苔黃膩，脈搏滑數。\n“”“\n\n"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {"role": "system", "content": initial_prompt},
            {"role": "user", "content": summary},
        ],
        temperature=0,
    )
    return response.choices[0].message


def generate_traumatology_history(summary: str) -> str:
    initial_prompt = '你是一個中醫師助理，請將以下內容轉變成病史。切記內容要準確，不可以擅自增添內容，，，要用繁體字：\n\n輸出格式：\n主訴：\n現病史：\n專科檢查\n\n參考以下案例”“”\n[總結1：\n- 頸椎疼痛已有8年\n- 左手臂麻木\n- 2006年底開始頸肩疼痛\n- 2007年9月頸肩和右手臂疼痛加重\n- 診斷為椎間盤突出\n- 2007年10月和11月接受中西醫結合治療\n- 2008年11月再次接受治療\n- 2008年初右手大拇指腫、麻木\n- 4月至6月嘗試牽引和按摩無效\n- 使用拔罐、刮痧和貼膏藥維持\n- 2009年頸肩不適和手指麻木加重\n- 2012年10月中旬手指麻木嚴重，右手臂開始麻木\n- 擠壓試驗和分離試驗陽性\n- MRI顯示椎間盤突出，硬膜囊受壓，椎管變窄\n- 診斷為神經根型頸椎病]\n\n[病史1：\n主訴:\n頸椎疼痛8年左右,伴有左上肢麻木.\n現病史:\n2006年末，頸肩有痛感,貼膏藥維持，2007年9月,頸肩、右臂疼痛難忍，某骨科醫院診斷:椎間盤突出,冷敷、打封閉、痛不止.空軍總醫院中西醫結合正骨治療科劉益善2007年10月,來某醫院中西醫結合正骨科,靜滴甘露醇、川穹等，口服頸舒顆粒,手法治療，於11月初解除疼痛，但頸肩仍不適,出院。 2008年11月初,來某醫院正骨科坐鞏固治療,方法與2007年同,2007年12月初出院。 2008年初，除頸肩仍不適外，右手大拇指尖腫、麻木,4-6月採用牽引、按摩方法連續三個月無效，後採用拔罐、刮痧、貼膏藥維持,至11月來某醫院專治手指麻木,12月出院時麻木減輕.2009年，全年頸肩不適,上邊年右手大拇指、食指、中指均麻木，至下半年逐漸加重,指尖知覺漸弱，同時，左手大拇指、食指、與右手相同麻木，個別時期，兩手十個手指均不同程度麻木，直至2012年初。 2012年10月中旬,兩手手指麻木加劇，右臂亦開始麻木\n專科檢查:\n1擠壓試驗，頸部和上肢出現疼痛加重,即為陽性.\n2分離試驗,頸部和上肢疼痛減輕，即為陽性。\n3MRI檢查,2～3  3~4  4～5  5~6  6~7椎間盤突出，硬膜囊受壓明顯,椎管明顯狹窄。\n診斷:\n神經根型頸椎病]\n\n\n[總結2：\n- 脖子疼了20天，最近4天加重\n- 無明顯原因\n- 吃活血止痛藥後疼痛減輕，停藥後加重\n- 頸椎MRI發現C6-7椎間盤突出\n- 脖子活動受限，偶爾頭痛頭暈\n- 舌紅，舌苔白，脈細數\n- 精神、睡眠、飲食、大小便正常，體重無變化\n- 脖子僵硬，脊柱無明顯彎曲\n- 右側風池穴和頸1椎體壓痛\n- 椎間孔擠壓試驗陽性，旋頸試驗陽性，臂叢神經牽拉試驗陽性\n- 肱二、三頭肌腱反射正常，閉目難立試驗陰性，霍夫曼氏徵陰性]\n\n[病史2：\n主訴：\n患者脖子疼痛已有20天，最近4天疼痛加重。\n\n現病史：\n患者脖子疼痛無明顯原因，曾經服用活血止痛藥後疼痛減輕，但停藥後疼痛加重。頸椎MRI檢查發現C6-7椎間盤突出。患者脖子活動受限，偶爾出現頭痛和頭暈。舌紅，舌苔白，脈細數。患者精神、睡眠、飲食、大小便正常，體重無變化。\n\n專科檢查：\n脖子僵硬，脊柱無明顯彎曲。右側風池穴和頸1椎體有壓痛感。椎間孔擠壓試驗陽性，旋頸試驗陽性，臂叢神經牽拉試驗陽性。肱二、三頭肌腱反射正常，閉目難立試驗陰性，霍夫曼氏徵陰性。\n\n診斷：\n根據病史和檢查結果，患者被診斷為神經根型頸椎病。 ]\n\n\n[總結3：\n-右肩疼半年，活動受限\n-疼痛加重，鈍痛\n-遇到寒冷是加劇\n-疼痛向頸部和右手臂放射\n-晚上疼痛影響睡覺\n-梳頭、穿衣、洗臉動作難以完成\n-診斷為肩周炎（右肩）\n-舌頭顏色淡，舌苔白，脈搏緊\n-右肩關節MRI顯示肌腱損傷、肱二頭肌長頭腱損傷，滑囊積液，炎症]\n[病史3：\n主訴：\n右肩關節疼痛，活動受限半年餘。\n現病史：\n患者述半年前受涼、勞累後出現右側肩關節疼痛，活動時疼痛加重，怕冷，遇寒 加重，肩關節活動略受限。近期感疼痛加重，呈持續性鈍痛，氣候變化或勞累後疼痛加重，時向頸部及右上 肢放射痛，肩痛晝輕夜重，並伴活動受限，梳頭、穿衣、洗臉等動作難以完成。右側肩關節周圍疼痛，夜間痛甚，影響睡眠，以肩後部疼痛較甚，時向頸部及右上肢放 射痛，肩痛晝輕夜重，怕冷，遇寒加重，外展、上舉、外旋活動受限，\n專科檢查：\n右肩關節MRI顯示肌腱損傷、肱二頭肌長頭腱損傷，滑囊積液，炎症。 ]\n\n"""'
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {"role": "system", "content": initial_prompt},
            {"role": "user", "content": summary},
        ],
        temperature=0,
    )
    return response.choices[0].message


@app.post("/generate_clinical_history")
def generate_history_endpoint(summary_input: SummaryInput):
    result = generate_clinical_history(summary_input.summary)
    formatted_result = json.dumps(
        {"content": result, "role": "assistant"}, ensure_ascii=False, indent=2
    )
    return formatted_result


@app.post("/generate_differential_diagnosis")
def generate_differential_diagnosis_endpoint(summary_input: SummaryInput):
    result = generate_differential_diagnosis(summary_input.summary)
    formatted_result = json.dumps(
        {"content": result, "role": "assistant"}, ensure_ascii=False, indent=2
    )
    return formatted_result


@app.post("/generate_obgyn_history")
def generate_obgyn_history_endpoint(summary_input: SummaryInput):
    result = generate_obgyn_history(summary_input.summary)
    formatted_result = json.dumps(
        {"content": result, "role": "assistant"}, ensure_ascii=False, indent=2
    )
    return formatted_result


@app.post("/generate_traumatology_history")
def generate_traumatology_history_endpoint(summary_input: SummaryInput):
    result = generate_traumatology_history(summary_input.summary)
    formatted_result = json.dumps(
        {"content": result, "role": "assistant"}, ensure_ascii=False, indent=2
    )
    return formatted_result
