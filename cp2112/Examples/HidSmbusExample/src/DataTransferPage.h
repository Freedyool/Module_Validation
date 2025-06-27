#pragma once

/////////////////////////////////////////////////////////////////////////////
// Includes
/////////////////////////////////////////////////////////////////////////////

#include "SLABCP2112.h"

/////////////////////////////////////////////////////////////////////////////
// CDataTransferPage dialog
/////////////////////////////////////////////////////////////////////////////

class CDataTransferPage : public CDialog
{
	DECLARE_DYNAMIC(CDataTransferPage)

public:
	CDataTransferPage(HID_SMBUS_DEVICE* pHidSmbus, CWnd* pParent = NULL);   // standard constructor
	virtual ~CDataTransferPage();

// Dialog Data
	enum { IDD = IDD_PROPPAGE_DATA_TRANSFER };

// Control Variables
protected:
	BYTE		m_slaveAddress = 0;
	WORD		m_bytesToRead = 0;
	BYTE		m_addressedSlaveAddress = 0;
	BYTE		m_targetAddressSize = 0;
	CString		m_targetAddressString;
	WORD		m_addressedBytesToRead = 0;
	WORD		m_forceBytesToRead = 0;
	CString		m_receiveData;
	CString		m_transmitData;
	BYTE		m_writeSlaveAddress = 0;

// Public Methods
public:
	void SetDefaults();
	void SetFromDevice();

// Protected Members
protected:
	HID_SMBUS_DEVICE* m_pHidSmbus;

// Protected Methods
protected:
	virtual void DoDataExchange(CDataExchange* pDX);    // DDX/DDV support
	void CustomDataExchange(CDataExchange* pDX);

	BOOL GetTargetAddress(BYTE targetAddress[HID_SMBUS_MAX_TARGET_ADDRESS_SIZE]);
	BOOL GetWriteData(BYTE writeData[HID_SMBUS_MAX_WRITE_REQUEST_SIZE], BYTE& size);

	void ReadRequest();
	void AddressReadRequest();
	void ForceReadResponse();
	void GetReadResponse();
	void WriteRequest();
	void CancelTransfer();
	void GetTransferStatus();

	void OutputStatus(CString functionName, HID_SMBUS_STATUS status);

// Message Handlers
protected:
	DECLARE_MESSAGE_MAP()
	afx_msg void OnBnClickedOk();
	afx_msg void OnBnClickedCancel();
	afx_msg void OnBnClickedButtonReadRequest();
	afx_msg void OnBnClickedButtonAddressReadRequest();
	afx_msg void OnBnClickedButtonForceReadResponse();
	afx_msg void OnBnClickedButtonGetReadResponse();
	afx_msg void OnBnClickedButtonWriteRequest();
	afx_msg void OnBnClickedButtonCancelTransfer();
	afx_msg void OnBnClickedButtonGetTransferStatus();
};
