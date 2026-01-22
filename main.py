# TO RUN THIS FILE TYPE : uvicorn main:app --reload
from fastapi import FastAPI, Path ,HTTPException , Query
from fastapi.responses import JSONResponse
import json
from pydantic import BaseModel , Field , computed_field
from typing import Annotated , Literal ,Optional

app = FastAPI()

class Patient(BaseModel):
    
    id : Annotated[str, Field(..., description= "atient ID field" ,example=" P000")]
    name:Annotated[str , Field(..., description="name of the patient")]
    age : Annotated[int , Field(..., gt= 0 ,lt =120, description="enter your age" )]
    height : Annotated[float , Field(...,description = "enter your height in meter")]
    weight : Annotated[float , Field(...,description = "enter your weight in kg")]
    city : Annotated[str , Field(...,description = "enter your city")]
    gender : Annotated[Literal['male','female','others'], Field(...)]
    
    @computed_field
    @property
    def bmi(self)->float:
        bmi = round(self.weight/(self.height**2),2)
        return bmi
    
    @computed_field
    @property
    def verdict(self)-> str:
        if self.bmi < 18.5:
            return"under weight"
        elif self.bmi < 25:
            return "Normal"
        elif self.bmi < 30 :
            return "healthy"
        else:
            return "obese"
    
#fucntion to load the data
def load_data():
    with open("patients.json" , "r") as f:
        data = json.load(f)
    return data
def save_data(data):
    with open("patients.json" , "w") as f:
        json.dump(data,f)
    
#home page of the website       
@app.get("/")
def hello():
    return {'call' : "patient management system"}
#about section
@app.get("/about")
def about():
    return ('patient data')
#page to view data
@app.get("/view")
def view():
    return(load_data())

#function to seach the patient by their id 
@app.get("/patient/{patient_id}")
def view_patient(patient_id : str = Path(..., description = "patient id dalo", example = "P001")):
    data = load_data()
    
    if patient_id in data: 
        # searching patient id in the data
            return data[patient_id]
        #if not found raise an error 
    raise HTTPException (status_code=404 , detail = "no patient data is available for this id ")

#function to sort the patient data accdoring to the need
@app.get("/sort")
def sort_patients(sort_by: str =Query(..., description = 'Sort on basis of height ,weight , bmi ') ,
                  order : str = Query("asc", description = "order ethier accending or decending")):
    valid_fields= ["height" , "weight" , "bmi"]
    
    if sort_by not in valid_fields:
        raise HTTPException(status_Code=400 , 
                            details= f'invalid field select from {valid_fields}')
    if order not in['asc' , 'desc']:
        raise HTTPException(status_code=400, 
                            detail=f'invalid field select from asc and desc')
        
    
    data = load_data()
    sort_order = True if order =="desc" else False
    sorted_data = sorted(data.values(), key = lambda x :x.get(sort_by,0), reverse =sort_order)
    return sorted_data
        
@app.post("/create")
def create_patient(patient :Patient):
    # loading the data
    data = load_data()
    
    #checking if patient already exist
    if patient.id in data:
        raise HTTPException(status_code=400, detail="Patient already exists")    
    
    # this is adding the details of new user into a data dictionary but value is everything except id and then 
    # we  are storing that data with respect to id as the key for that data
    # model_dump convert a pydantic object into a dict so we used that but excluded the id
    
    data[patient.id] = patient.model_dump(exclude=["id"])
    
    save_data(data) # this updates json
    
    return JSONResponse(status_Code = 201 , content={"messege":'patient created succesfully'})



class PatientUpdate(BaseModel):
    id : Annotated[Optional[str], Field(default = None)]
    name : Annotated[Optional[str],Field(default = None)]
    city :Annotated[Optional[str],Field(default =None)]
    gender : Annotated[Optional[Literal["male","female","other"]],Field(default =None)]
    age : Annotated[Optional[int],Field(default=None)]
    height : Annotated[Optional[float],Field(default = None)]
    weight : Annotated[Optional[float],Field(default = None)]

@app.put("/update/{patient_id}")
def updated_patient(patient_id : str, patient_update:PatientUpdate):
    data = load_data()
    if patient_id not in data:
        raise HTTPException(status_code= 404,detail="patient not found")
    else:
        existing_patient_info = data[patient_id]
        updated_patient_info = patient_update.model_dump(exclude_unset=True)
        
        for key ,values in updated_patient_info.items():
            existing_patient_info[key] = values
        # Now   
        existing_patient_info["id"] = patient_id
        
        existing_patient_obj = Patient(**existing_patient_info)
        existing_patient_info =existing_patient_obj.model_dump(exclude=["id"])
        
        data[patient_id] = existing_patient_info
        save_data(data)
        return JSONResponse(status_code = 201,content={"messege":"updated Succesfully"})

@app.delete("/delete/{patient_id}")

def delete_patient(patient_id = str):
    data = load_data()
    if patient_id not in data:
        raise HTTPException(status_code=404,detail="patient not found")
    
    del data[patient_id]
    save_data(data)
    return JSONResponse(status_code= 201,content={"message":"patient deleted successfully"})

# I will be uploading new project about how we can use FastAPI to create APIs for a ML model
            
        
    
            
        
    
