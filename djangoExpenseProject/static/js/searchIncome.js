const searchField = document.querySelector("#searchField");
const tableOutPut = document.querySelector(".table-output");
const appTable = document.querySelector(".app-table");
const paginationContainer = document.querySelector(".pagination-container");
const tableBody = document.querySelector(".table-body");


tableOutPut.style.display = "none";
searchField.addEventListener("keyup",(e)=>{
    const searchValue = e.target.value;

    if(searchValue.trim().length > 0){
        console.log(searchField);
        fetch("/income/search-income", {
            body: JSON.stringify({ searchText: searchValue}),
            method: "POST",
        })
            .then((response) => response.json())
            .then((data) => {
                tableBody.innerHTML = "";
                tableOutPut.style.display = "block";
                appTable.style.display = "none";
                paginationContainer.style.display = "none";
                tableBody.innerHTML="";
                if(data.length === 0){
                    tableOutPut.innerHTML = "No result found";
                }else{
                    data.forEach((item) => {
                        tableBody.innerHTML += `
                            <tr>
                                <td>${item.amount}</td>
                                <td>${item.source}</td>
                                <td>${item.description}</td>
                                <td>${item.date}</td>
                            </tr>
                        `;
                    });
                }
            }
            )
    }else{
        tableOutPut.style.display = "none";
        appTable.style.display = "block";
        paginationContainer.style.display = "block";

    }
})