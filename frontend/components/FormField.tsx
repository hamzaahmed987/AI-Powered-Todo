'use client';

import { IoAlertCircle, IoMailOutline, IoLockClosedOutline, IoPerson } from 'react-icons/io5';

interface FormFieldProps {
  field: {
    name: string;
    value: any;
    onChange: (e: any) => void;
    onBlur: (e: any) => void;
  };
  form: {
    errors: Record<string, string>;
    touched: Record<string, boolean>;
  };
  label?: string;
  placeholder?: string;
  type?: string;
  rows?: number;
  helperText?: string;
  disabled?: boolean;
  className?: string;
  required?: boolean;
}

export function FormField({
  field,
  form: { errors, touched },
  label,
  placeholder,
  type = 'text',
  rows,
  helperText,
  disabled = false,
  className = '',
  required = false,
  ...props
}: FormFieldProps) {
  const { name, value } = field;
  const error = touched[name] && errors[name];
  const hasError = !!error;

  const getFieldIcon = () => {
    switch (field.name.toLowerCase()) {
      case 'email':
        return <IoMailOutline className="w-5 h-5" />;
      case 'password':
      case 'confirmpassword':
        return <IoLockClosedOutline className="w-5 h-5" />;
      case 'name':
        return <IoPerson className="w-5 h-5" />;
      default:
        return null;
    }
  };

  const fieldIcon = getFieldIcon();

  const baseInputClass = `
    w-full px-4 py-3 border-2 rounded-lg transition-all
    focus:outline-none focus:ring-2 focus:ring-offset-0
    disabled:bg-gray-100 disabled:cursor-not-allowed disabled:text-gray-400 disabled:border-gray-300
    ${hasError
      ? 'border-red-400 focus:ring-red-400 focus:border-red-400 bg-red-50 text-red-700'
      : 'border-gray-200 focus:ring-blue-500 focus:border-blue-500 bg-white text-gray-900 placeholder-gray-400'
    }
    text-sm font-medium
    ${fieldIcon ? 'pl-10' : ''}
  `;

  return (
    <div className="w-full">
      {label && (
        <label
          htmlFor={name}
          className="block text-gray-700 font-semibold mb-1.5 text-sm"
        >
          {label}
        </label>
      )}

      {type === 'textarea' ? (
        <textarea
          id={name}
          {...field}
          placeholder={placeholder}
          disabled={disabled}
          rows={rows || 3}
          className={`${baseInputClass} resize-none ${className}`}
          {...props}
        />
      ) : (
        <div className="relative">
          {fieldIcon && (
            <div className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none flex items-center">
              {fieldIcon}
            </div>
          )}
          <input
            id={name}
            type={type}
            {...field}
            placeholder={placeholder}
            disabled={disabled}
            className={`${baseInputClass} ${className}`}
            {...props}
          />
        </div>
      )}

      {hasError && (
        <p className="text-red-600 text-xs mt-2 font-semibold flex items-center gap-1.5">
          <IoAlertCircle className="w-4 h-4 flex-shrink-0" />
          {String(error)}
        </p>
      )}

      {helperText && !hasError && (
        <p className="text-gray-500 text-xs sm:text-sm mt-2 italic">{helperText}</p>
      )}
    </div>
  );
}
