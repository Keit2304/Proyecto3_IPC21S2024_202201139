from flask import Flask, request, jsonify
from flask_cors import CORS
from xml.etree import ElementTree as ET
from listas import Cliente,Bancos,facturas,pagos
import re
import copy

app = Flask(__name__)
CORS(app)
misFacturas = facturas()
misclientes = Cliente()
misbancos = Bancos()
mispagos = pagos()

listacodBancos = []
listaNits = []
#me falta parsear la fecha   <---------------


#-------------------- AQUI TRABAJAREMOS LOS ENDPOINTS --------------------

#---------------------- CARGA DE ARCHIVOS --------------------------------
def generarSalidaTransacciones():
        
        salida = ""
        salida += "<?xml version='1.0'?>\n"
        salida += f"<transacciones> \n"
        salida += f"<facturas> \n"
        salida += f"    <nuevasFacturas> {misFacturas.contadorFactura} </nuevasFacturas>\n"
        salida += f"    <facturasDuplicadas> {misFacturas.duplicadaFactura} </facturasDuplicadas>\n"
        salida += f"    <facturasConError> {misFacturas.FacturaError} </facturasConError>\n"
        salida += f"</facturas>\n"
        salida += f"<pagos> \n"
        salida += f"    <nuevosPagos> {mispagos.contadorPago} </nuevosPagos>\n"
        salida += f"    <pagosDuplicados> {mispagos.duplicadoPago} </pagosDuplicados>\n"
        salida += f"    <pagosConError> {mispagos.pagoError} </pagosConError>\n"
        salida += f"</pagos>\n"
        salida += f"</transacciones>\n"
        return salida
        

def generarSalidaConfig():
    salida = ""
    salida += "<?xml version='1.0'?>\n"
    salida += f"<respuesta> \n"
    salida += f"<clientes> \n"
    salida += f"    <creados> {misclientes.contadorCliente} </creados>\n"
    salida += f"    <actualizados> {misclientes.contadorClienteActualizar} </actualizados>\n"
    salida += f"</clientes>\n"
    salida += f"<bancos> \n"
    salida += f"    <creados> {misbancos.contadorbancos} </creados>\n"
    salida += f"    <actualizados> {misbancos.contadorBancoActualizados} </actualizados>\n"
    salida += f"</bancos>\n"
    salida += f"</respuesta>\n"
    return salida

@app.route('/cargarTransaccion', methods=['POST'])
def cargarTransaccion():
    try:
        patron_fecha = r'\d{2}/\d{2}/\d{4}' # Expresión regular para encontrar fechas en formato DD/MM/YYYY

        entradaXML = request.data #OBTENER EL XML DE LA PETICION
        decodificado = entradaXML.decode('utf-8') #DECODIFICAR EL XML
        

        xmlRecibido = ET.XML(decodificado) #convertir el xml a un objeto de ElementTree

        for factura in xmlRecibido.find('facturas').iter('factura'):
            numfactura = factura.find('numeroFactura').text.strip().replace('"','')
            nitClienteFactura = factura.find('NITcliente').text.strip().replace('"','')
            fechaFactura = factura.find('fecha').text.strip().replace('"','')
            montoFactura = factura.find('valor').text.strip()
            
            resultado = re.search(patron_fecha, fechaFactura)
            if resultado:   
                fechaFactura = resultado.group(0)
            else:
                fechaFactura = fechaFactura


            extraccionMonto = re.search(r'Q(.*)', montoFactura)
            if extraccionMonto:
                montoFactura = extraccionMonto.group(1)
            else:
                montoFactura = montoFactura
            
            numero_nit = re.search(r':\s*(\w+)', nitClienteFactura) 
            if numero_nit:
                nitClienteFactura = numero_nit.group(1)
            else:
                nitClienteFactura = nitClienteFactura

            
            if nitClienteFactura not in listaNits:
                print("Cliente no encontrado ", nitClienteFactura)
                misFacturas.FacturaError += 1 
                
            else:
                estado = misFacturas.factura_duplicada(numfactura) # de lo contrario verificamos que no sea duplicada
                if estado:
                    print("Factura duplicada") # si si es, queda ahi xd
                else:
                    misFacturas.agregar_factura(numfactura, nitClienteFactura, fechaFactura, float(montoFactura)) # si no, se agregara la factura
                
        for pago in xmlRecibido.find('pagos').iter('pago'):
            codBanco = pago.find('codigoBanco').text.strip()
            fechaPago = pago.find('fecha').text.strip().replace('"','')
            nitClientePago = pago.find('NITcliente').text.strip().replace('"','')
            montoPago = pago.find('valor').text.strip()

            resultadoP = re.search(patron_fecha, fechaPago)
            if resultadoP:
                fechaPago = resultadoP.group(0)
            else:
                fechaPago = fechaPago


            extraccionMontoP = re.search(r'Q(.*)', montoPago)
            if extraccionMontoP:
                montoPago = extraccionMontoP.group(1)
            else:
                montoPago = montoPago

            numero_nit2 = re.search(r':\s*(\w+)', nitClientePago) 
            if numero_nit2:
                nitClientePago = numero_nit2.group(1) 
            else:
                nitClientePago = nitClientePago

            if int(codBanco) not in listacodBancos or nitClientePago not in listaNits:  
                print("Banco no encontrado ", codBanco, "Cliente no encontrado ", nitClientePago)
                mispagos.pagoError += 1
                
            else:
                estadoP = mispagos.pago_duplicado(int(codBanco),nitClientePago,fechaPago) # verificar si esta duplicada
                if estadoP:
                    print("Pago duplicado") # si lo esta, ahi queda xd
                else:
                    mispagos.agregar_pago(int(codBanco), fechaPago, nitClientePago, float(montoPago)) # si no,
            

        respu = generarSalidaTransacciones()
        return respu, 200

    except Exception as e:
        salida = ""
        salida += "<?xml version='1.0'?>\n"
        salida += f"<Error> \n"
        salida += f"<DatosErroneos> Vuelve a intentarlo </DatosErroneos>\n"
        salida += f"</Error>\n" 
        print(e)
        return salida, 400      

@app.route('/cargarConfiguracion', methods=['POST'])
def cargarConfiguracion():
    try:
        entradaXML = request.data #OBTENER EL XML DE LA PETICION
        decodificado = entradaXML.decode('utf-8') #DECODIFICAR EL XML
        xmlRecibido = ET.XML(decodificado) #convertir el xml a un objeto de ElementTree

        for cliente in xmlRecibido.find('clientes').iter('cliente'):
            nitCliente = cliente.find('NIT').text.strip().replace('"','')
            nombreCliente = cliente.find('nombre').text.strip().replace('"','')
            

            numero_nit2 = re.search(r':\s*(\w+)', nitCliente) 
            if numero_nit2:
                nitCliente = numero_nit2.group(1)
            else:
                nitCliente = nitCliente
                
            estadoC = misclientes.actualizar_cliente(nitCliente, nombreCliente)
            if estadoC:
                print("Cliente actualizado")
            else:
                misclientes.agregar_cliente(nitCliente, nombreCliente)
                listaNits.append(nitCliente)
            

        for banco in xmlRecibido.find('bancos').iter('banco'):
            codigoBanco = banco.find('codigo').text.strip()
            nombreBanco = banco.find('nombre').text.strip().replace('"','')
            estadoB =  misbancos.actualizar_banco(int(codigoBanco), nombreBanco)
            if estadoB:
                print("Banco actualizado")
            else:
                misbancos.agregar_banco(int(codigoBanco), nombreBanco)
                listacodBancos.append(int(codigoBanco))
           
        print(misclientes.cliente)
        print(misbancos.bancos)
        respu = generarSalidaConfig()
        return respu, 200
    except Exception as e:
        salida = ""
        salida += "<?xml version='1.0'?>\n"
        salida += f"<Error> \n"
        salida += f"<DatosErroneos> Vuelve a intentarlo </DatosErroneos>\n"
        salida += f"</Error>\n" 
        print(e)
        return salida, 400 


@app.route('/getTransacciones', methods=['GET']) #en formato JSON
def getTransacciones():
    facturaL = []
    pagoL = []
    for pag in mispagos.pagos:
        pagoL.append({'codBanco': pag[0], 'fecha': pag[1], 'nitCliente': pag[2], 'valor': pag[3]})

    for transac in misFacturas.facturas:
        facturaL.append({'numFactura': transac[0], 'nitCliente': transac[1], 'fecha': transac[2], 'valor': transac[3]})

    #unir ambos diccionarios
    facturaL.extend(pagoL)
    return jsonify(facturaL)

@app.route('/getConfiguracion', methods=['GET']) #en formato JSON
def getConfiguracion():
    bancoL = []
    clienteL = []
    for banc in misbancos.bancos:
        bancoL.append({'codigo': banc[0], 'nombre': banc[1]})

    for clien in misclientes.cliente:
        clienteL.append({'nit': clien[0], 'nombre': clien[1]})

    #unir ambos diccionarios
    clienteL.extend(bancoL)
    return jsonify(clienteL)


@app.route('/consultarEstadoClientes/<string:nit>', methods=['GET']) #en formato JSON
def consultarEstadoClientes(nit):
    try:
        transaccioness = []
        datos = []
        datos2 = []
        dato1 = []
        nitcliente = misclientes.getNitCliente(nit)
        nombrecliente = misclientes.getNombreCliente(nit)
        


        pagosT = mispagos.getPagosSegunNitCliente(nit)
        facturasT = misFacturas.getFacturaSegunNitCliente(nit)
        
        pagosFacturas = mispagos.montoPagosNitCliente(nit)-misFacturas.montoFacturasNitCliente(nit) 
        
        dato1.append({'nombre': nombrecliente, 'Nit': nitcliente, 'saldo': pagosFacturas})
        

        for pago in range(len(pagosT)):
            if pagosT[pago][2] == nitcliente:
                banco = misbancos.getNombreBanco(pagosT[pago][0])
                datos.append({'fecha': pagosT[pago][1], 'abono': f"Q{pagosT[pago][3]}", 'banco': banco})



        for factura in range(len(facturasT)):
            if facturasT[factura][1] == nitcliente:
                datos2.append({'fecha': facturasT[factura][2], 'cargo': f"Q{facturasT[factura][3]}"})
        
        
        
        transaccioness = dato1 + datos + datos2
        return jsonify(transaccioness), 200
    except Exception as e:
        print(e)
        return jsonify({'Error': 'Cliente no encontrado , intenta de nuevo'}), 400


#-------------------------LIMPIAR DATOS ---------------------------------
@app.route('/limpiarDatosConfig', methods=['DELETE'])
def limpiarDatosConfig():
    misbancos.limpiar()
    misclientes.limpiar()
    print(misbancos.bancos)
    print(misclientes.cliente)
    root = ET.Element('DatosLimpiados')
    root.text = 'Datos limpiados'
    return ET.tostring(root, encoding='utf8',method='xml'), 200

@app.route('/limpiarDatosTransacciones', methods=['DELETE'])
def limpiarDatosTransacciones():
    misFacturas.limpiar()
    mispagos.limpiar()
    
    
    misFacturas.montoFacrura = 0
    mispagos.montoPago = 0
    print(misFacturas.montoFacrura)
    print(mispagos.montoPago)
    root = ET.Element('DatosLimpiados')
    root.text = 'Datos limpiados'
    return ET.tostring(root, encoding='utf8',method='xml'), 200





@app.route('/consultarEstadoCliente/<string:nit>', methods=['GET'])
def consultarEstadoCliente(nit):
    try:
        salida = ""
        nitcliente = misclientes.getNitCliente(nit)
        nombrecliente = misclientes.getNombreCliente(nit)


        salida += f"Cliente: {nombrecliente}    NIT: {nitcliente}\n"
        pagosT = mispagos.getPagosSegunNitCliente(nit)
        facturasT = misFacturas.getFacturaSegunNitCliente(nit)
        
        pagosFacturas = mispagos.montoPagosNitCliente(nit)-misFacturas.montoFacturasNitCliente(nit) 
        
        salida += f"Saldo: {pagosFacturas}"

        if pagosFacturas < 0:
            salida += " (Deudor)\n"
        else:
            salida += " (Acreedor)\n"


        salida += "Transacciones: \n"
        salida += "\n"
        salida += "Fecha                Cargo           Abono               Banco\n"

        for pago in range(len(pagosT)):
            if pagosT[pago][2] == nitcliente:
                banco = misbancos.getNombreBanco(pagosT[pago][0])
                salida += f"{pagosT[pago][1]}                           Q{pagosT[pago][3]}             {banco}\n"



        for factura in range(len(facturasT)):
            if facturasT[factura][1] == nitcliente:
                salida += f"{facturasT[factura][2]}        Q{facturasT[factura][3]}\n"
        
        
        return salida
    except Exception as e:
        print(e)
        salida = "Cliente no encontrado , intenta de nuevo"
        return salida


        



@app.route('/mostrarTodos', methods=['GET'])
def mostrarTodos(): 
    
    try:
        salida = ""
        salida += "INFOMRACION SOBRE TODOS LOS CLIENTES: \n"
        salida += "------------------------------------------------------------\n"
        for cliente in misclientes.cliente:

            nitcliente = cliente[0]
            nombrecliente = cliente[1]
            print("**************************************************")
            print("NIT CLIENTE: ",nitcliente)
            salida += f"Cliente: {nombrecliente}    NIT: {nitcliente}\n"
            pagosT = mispagos.getPagosSegunNitCliente(nitcliente)
            facturasT = misFacturas.getFacturaSegunNitCliente(nitcliente)
            print("EEEEEEEEEEEE :",pagosT)
            print("PPPPPPPPPPPPPPP: ",facturasT)
            print("**************************************************")

            pagosFacturas = mispagos.montoPagosNitCliente(nitcliente)-misFacturas.montoFacturasNitCliente(nitcliente) 
            
            salida += f"Saldo: {pagosFacturas}"

            if pagosFacturas < 0:
                salida += " (Deudor)\n"
            else:
                salida += " (Acreedor)\n"


            salida += "Transacciones: \n"
            salida += "\n"
            salida += "Fecha                Cargo           Abono               Banco\n"

            for pago in range(len(pagosT)):
                if pagosT[pago][2] == nitcliente:
                    banco = misbancos.getNombreBanco(pagosT[pago][0])
                    salida += f"{pagosT[pago][1]}                           Q{pagosT[pago][3]}             {banco}\n"



            for factura in range(len(facturasT)):
                if facturasT[factura][1] == nitcliente:
                    salida += f"{facturasT[factura][2]}        Q{facturasT[factura][3]}\n"
            
            salida += "\n"
            salida += "------------------------------------------------------------\n"
            
        return salida
    except Exception as e:
        print(e)
        salida = "No se pudo cargar la informacion , intenta de nuevo"
        return salida




@app.route('/graficar', methods=['GET']) #en formato JSON
def graficar():

    try: 
        tipobanco = []
        montoPorBanco = []
        mesPago = []
        todoI = []
        pagosTempo = []
        pagosTempo = copy.deepcopy(mispagos.pagos)
        
        patron = r"(\d{2}/\d{4})"
        for fecha in pagosTempo:
            resultado = re.search(patron, fecha[1])
            if resultado:
                fecha[1] = resultado.group(0)
            else:
                fecha[1] = fecha[1]
        

    
        
        for pago in pagosTempo:
            if pago[1] not in mesPago and pago[0] not in tipobanco: # si el mes no esta en la lista y el banco no esta en la lista
                mesPago.append(pago[1])
                tipobanco.append(pago[0])
                montoPorBanco.append(pago[3])
                
            elif pago[1] not in mesPago and pago[0] in tipobanco: # si el mes no esta en la lista y el banco si esta en la lista
                mesPago.append(pago[1])
                tipobanco.append(pago[0])
                montoPorBanco.append(pago[3])
            
            

            else:
                index = mesPago.index(pago[1])
                montoPorBanco[index] += pago[3]

      


        

        for banco in misbancos.bancos:
            for i in range(len(tipobanco)):
                if banco[0] == tipobanco[i]:
                    tipobanco[i] = banco[1]
                
           
        
        patron2 = r"(\d{2})/\d{4}"
        for i in range(len(mesPago)):
            resultado = re.search(patron2, mesPago[i])
            if resultado:
                mesPago[i] = resultado.group(1)
            else:
                mesPago[i] = mesPago[i]

        for tipomes in range(len(mesPago)):
            if mesPago[tipomes] == "01":
                mesPago[tipomes] = "ENERO"
            elif mesPago[tipomes] == "02":
                mesPago[tipomes] = "FEBRERO"
            elif mesPago[tipomes] == "03":
                mesPago[tipomes] = "MARZO"
            elif mesPago[tipomes] == "04":
                mesPago[tipomes] = "ABRIL"
            elif mesPago[tipomes] == "05":
                mesPago[tipomes] = "MAYO"
            elif mesPago[tipomes] == "06":
                mesPago[tipomes] = "JUNIO"
            elif mesPago[tipomes] == "07":
                mesPago[tipomes] = "JULIO"
            elif mesPago[tipomes] == "08":
                mesPago[tipomes] = "AGOSTO"
            elif mesPago[tipomes] == "09":
                mesPago[tipomes] = "SEPTIEMBRE"
            elif mesPago[tipomes] == "10":
                mesPago[tipomes] = "OCTUBRE"
            elif mesPago[tipomes] == "11":
                mesPago[tipomes] = "NOVIEMBRE"
            elif mesPago[tipomes] == "12":
                mesPago[tipomes] = "DICIEMBRE"
            else:
                mesPago[tipomes] = mesPago[tipomes]
            
        print(tipobanco)
        print(montoPorBanco)
        print(mesPago)
        todoI.append(tipobanco)
        todoI.append(montoPorBanco)
        todoI.append(mesPago)
        respuesta = {}

        #iterar todoI
        for i in range(len(todoI[2])):  
            respuesta[todoI[2][i]] = {'banco': todoI[0][i], 'monto': todoI[1][i]} # {'mes': {'banco': 1000, 'monto': 'Enero'}} [1][i] = monto [2][i] = mes

        
        return jsonify(respuesta), 200
    except Exception as e:
        print(e)
        return jsonify({'Error': 'Intenta de nuevo'}), 400
    

def meses(mes):
    meses = {
    "ENERO": ["ENERO", "FEBRERO", "MARZO"],
    "FEBRERO": ["FEBRERO", "MARZO", "ABRIL"],
    "MARZO": ["MARZO", "ABRIL", "MAYO"],
    "ABRIL": ["ABRIL", "MAYO", "JUNIO"],
    "MAYO": ["MAYO", "JUNIO", "JULIO"],
    "JUNIO": ["JUNIO", "JULIO", "AGOSTO"],
    "JULIO": ["JULIO", "AGOSTO", "SEPTIEMBRE"],
    "AGOSTO": ["AGOSTO", "SEPTIEMBRE", "OCTUBRE"],
    "SEPTIEMBRE": ["SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE"],
    "OCTUBRE": ["OCTUBRE", "NOVIEMBRE", "DICIEMBRE"],
    "NOVIEMBRE": ["NOVIEMBRE", "DICIEMBRE", "ENERO"],
    "DICIEMBRE": ["DICIEMBRE", "ENERO", "FEBRERO"]
    }


    return meses[mes]


@app.route('/misgraficas/<string:mes>', methods=['GET'])
def misgraficas(mes):

    try: 
        miMeses = meses(mes)
        print(miMeses)
        tipobanco = []
        montoPorBanco = []
        mesPago = []
        todoI = []
        pagosTempo = []
        pagosTempo = copy.deepcopy(mispagos.pagos)
        
        patron = r"(\d{2}/\d{4})"
        for fecha in pagosTempo:
            resultado = re.search(patron, fecha[1])
            if resultado:
                fecha[1] = resultado.group(0)
            else:
                fecha[1] = fecha[1]
        

    
        
        for pago in pagosTempo:
            if pago[1] not in mesPago : # si el mes no esta en la lista y el banco no esta en la lista
                mesPago.append(pago[1])
                tipobanco.append(pago[0]) 
                montoPorBanco.append(pago[3])

            elif pago[1] in mesPago and pago[0] not in tipobanco: # si el mes no esta en la lista y el banco si esta en la lista
                mesPago.append(pago[1])
                tipobanco.append(pago[0])
                montoPorBanco.append(pago[3])

            # elif pago[1] not in mesPago and pago[0] in tipobanco: # si el mes no esta en la lista y el banco si esta en la lista
            #     mesPago.append(pago[1])
            #     tipobanco.append(pago[0])
            #     montoPorBanco.append(pago[3])
            
          
            # SI SUMA SI TIENE AMBOS BANCOS Y FECHAS IGUALES :)
            else:
                
                index = mesPago.index(pago[1])
                montoPorBanco[index] += pago[3]

      
        for banco in misbancos.bancos:
            for i in range(len(tipobanco)):
                if banco[0] == tipobanco[i]:
                    tipobanco[i] = banco[1]
                # else:
                #     for j in range(len(tipobanco[i])):
                #         if banco[0] == tipobanco[i][j]:
                #             tipobanco[i][j] = banco[1]
                
        
        patron2 = r"(\d{2})/\d{4}"
        for i in range(len(mesPago)):
            resultado = re.search(patron2, mesPago[i])
            if resultado:
                mesPago[i] = resultado.group(1)
            else:
                mesPago[i] = mesPago[i]

        for tipomes in range(len(mesPago)):
            if mesPago[tipomes] == "01":
                mesPago[tipomes] = "ENERO"
            elif mesPago[tipomes] == "02":
                mesPago[tipomes] = "FEBRERO"
            elif mesPago[tipomes] == "03":
                mesPago[tipomes] = "MARZO"
            elif mesPago[tipomes] == "04":
                mesPago[tipomes] = "ABRIL"
            elif mesPago[tipomes] == "05":
                mesPago[tipomes] = "MAYO"
            elif mesPago[tipomes] == "06":
                mesPago[tipomes] = "JUNIO"
            elif mesPago[tipomes] == "07":
                mesPago[tipomes] = "JULIO"
            elif mesPago[tipomes] == "08":
                mesPago[tipomes] = "AGOSTO"
            elif mesPago[tipomes] == "09":
                mesPago[tipomes] = "SEPTIEMBRE"
            elif mesPago[tipomes] == "10":
                mesPago[tipomes] = "OCTUBRE"
            elif mesPago[tipomes] == "11":
                mesPago[tipomes] = "NOVIEMBRE"
            elif mesPago[tipomes] == "12":
                mesPago[tipomes] = "DICIEMBRE"
            else:
                mesPago[tipomes] = mesPago[tipomes]
            

        todoI.append(tipobanco)
        todoI.append(montoPorBanco)
        todoI.append(mesPago)
        respuesta = {}
        print("IIIIIIIIIIIIIIIIII  ",todoI)

         
        for mes in miMeses:
            for i in range(len(todoI[2])): 
                if todoI[2][i] == mes:
                    respuesta[todoI[2][i]] = {'banco': todoI[0][i], 'monto': todoI[1][i]} 
    
          
                    


        return jsonify(respuesta), 200
    except Exception as e:
        print(e)
        return jsonify({'Error': 'Intenta de nuevo'}), 400
    



if __name__ == '__main__':
    app.run(host='localhost',debug=True, port=5000)
